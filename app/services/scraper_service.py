import os
import re
import aiohttp
from bs4 import BeautifulSoup
from app.utils.storage_strategy import JSONStorageStrategy
from app.schemas.scraper_settings import ScraperSettings
from app.models.product_model import ProductModel
from cachetools import TTLCache
from dotenv import load_dotenv

load_dotenv()

class ScraperService:
    def __init__(self, image_directory: str, settings: ScraperSettings):
        self.settings = settings
        self.image_directory = image_directory
        self.storage_strategy = JSONStorageStrategy()
        self.cache = TTLCache(maxsize=1000, ttl=3600)  # Cache with TTL of 1 hour
        
        # Ensure the image directory exists
        os.makedirs(self.image_directory, exist_ok=True)

    async def fetch(self, url: str):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, ssl=False) as response:  # Disable SSL verification
                    return await response.text()
            except Exception as e:
                print(f"Failed to fetch {url}: {str(e)}")
                return None

    async def fetch_image(self, url: str, filename: str):
        file_path = os.path.join(self.image_directory, filename)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, ssl=False) as response:
                    if response.status == 200:
                        with open(file_path, 'wb') as f:
                            f.write(await response.read())
                        return file_path
                    else:
                        print(f"Failed to fetch image {url}: Status code {response.status}")
                        return "default_image_path"  # Provide a default path or empty string
            except Exception as e:
                print(f"Failed to fetch image {url}: {str(e)}")
                return "default_image_path"  # Provide a default path or empty string

    def extract_price(self, price_text: str) -> float:
        # Remove any non-numeric characters except for decimal points
        cleaned_price = re.sub(r'[^\d.,]', '', price_text)
        # Replace commas with dots for decimal point separation
        cleaned_price = cleaned_price.replace(',', '.')
        try:
            # Convert the cleaned price to a float
            return float(cleaned_price)
        except ValueError:
            # Print a warning if conversion fails and return default value 0.0
            print(f"Failed to convert price '{price_text}' to float")
            return 0.0

    async def scrape_page(self, page_number: int):
        url = f"https://dentalstall.com/shop/?page={page_number}"
        page_content = await self.fetch(url)
        if page_content is None:
            return []

        print(f"Page content for page {page_number}:\n{page_content[:1000]}...") 
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
                image_path = "default_image_path"  # Provide a default value or empty string

            # Log the title and price before cache check
            print(f"Product title: {title}, Price: {price}")

            # Check if the product is in the cache and if the price has changed
            if title in self.cache:
                if self.cache[title] == price:
                    print(f"Product {title} is already in cache with the same price. Skipping...")
                    continue  # Skip if the price hasn't changed

            # Add the product data to the cache
            self.cache[title] = price
            print(f"Added to cache: {title} with price {price}")
            print("IN cache",self.cache)
            print(f"Image URL: {img_url}")
            product_data = ProductModel(
                product_title=title,
                product_price=price,
                path_to_image=image_path
            )

            products.append(product_data.model_dump())

        return products

    async def scrape(self):
        all_products = []
        for page in range(1, self.settings.num_pages + 1):
            products = await self.scrape_page(page)
            all_products.extend(products)

        self.storage_strategy.save(all_products)
        print(f"Scraped {len(all_products)} products.")

    def get_cache(self):
        """Return the current cache as a dictionary."""
        return {key: value for key, value in self.cache.items()}

    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()
        print("Cache cleared")
