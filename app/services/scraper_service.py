import os
import re
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from app.utils.storage_strategy import JSONStorageStrategy
from app.schemas.scraper_settings import ScraperSettings
from app.models.product_model import ProductModel
from cachetools import TTLCache

class ScraperService:
    def __init__(self, image_directory: str, settings: ScraperSettings):
        self.settings = settings
        self.image_directory = image_directory
        self.storage_strategy = JSONStorageStrategy()
        self.cache = TTLCache(maxsize=1000, ttl=3600)
        
        # Ensure the image directory exists
        os.makedirs(self.image_directory, exist_ok=True)

    async def fetch(self, url: str, retries: int = 3, delay: int = 5):
        """Fetch content from a URL with retry mechanism."""
        attempt = 0
        while attempt < retries:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, ssl=False) as response:
                        if response.status == 200:
                            return await response.text()
                        else:
                            print(f"Failed to fetch {url}: Status code {response.status}")
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed to fetch {url}: {str(e)}")

            attempt += 1
            await asyncio.sleep(delay * (2 ** attempt))

        print(f"Failed to fetch {url} after {retries} attempts")
        return None

    async def fetch_image(self, url: str, filename: str):
        file_path = os.path.join(self.image_directory, filename)
        attempt = 0
        while attempt < 3:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, ssl=False) as response:
                        if response.status == 200:
                            with open(file_path, 'wb') as f:
                                f.write(await response.read())
                            return file_path
                        else:
                            print(f"Failed to fetch image {url}: Status code {response.status}")
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed to fetch image {url}: {str(e)}")

            attempt += 1
            await asyncio.sleep(5 * (2 ** attempt))

        return "default_image_path"

    def extract_price(self, price_text: str) -> float:
        """Extracts and converts the price text to a float value."""
        cleaned_price = re.sub(r'[^\d.,]', '', price_text)
        cleaned_price = cleaned_price.replace(',', '.')
        try:
            return float(cleaned_price)
        except ValueError:
            print(f"Failed to convert price '{price_text}' to float")
            return 0.0

    async def scrape_page(self, page_number: int):
        """Scrapes a single page and returns a list of product data."""
        url = f"https://dentalstall.com/shop/?page={page_number}"
        page_content = await self.fetch(url)
        if page_content is None:
            return []

        soup = BeautifulSoup(page_content, 'html.parser')
        products = []

        for product in soup.select(".product-inner.clearfix"):
            title_tag = product.select_one(".mf-product-details .woo-loop-product__title a")
            price_tag = product.select_one(".mf-product-price-box .price .woocommerce-Price-amount.amount bdi")
            img_tag = product.select_one(".mf-product-thumbnail img")

            title = title_tag.get_text(strip=True) if title_tag else "No Title"
            price_text = price_tag.get_text(strip=True) if price_tag else "0"
            price = self.extract_price(price_text)

            img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None

            if img_url:
                filename = img_url.split('/')[-1]
                image_path = await self.fetch_image(img_url, filename)
            else:
                image_path = "default_image_path"

            if title in self.cache and self.cache[title] == price:
                continue

            product_data = ProductModel(
                product_title=title,
                product_price=price,
                path_to_image=image_path
            )

            products.append(product_data.model_dump())
            self.cache[title] = price

        return products

    async def scrape(self):
        """Scrapes multiple pages and saves the product data."""
        all_products = []
        for page in range(1, self.settings.num_pages + 1):
            products = await self.scrape_page(page)
            all_products.extend(products)

        self.storage_strategy.save(all_products)

    def get_cache(self):
        """Return the current cache as a dictionary."""
        return {key: value for key, value in self.cache.items()}

    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()
        print("Cache cleared")
