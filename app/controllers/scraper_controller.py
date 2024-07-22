from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.scraper_settings import ScraperSettings
from app.services.scraper_service import ScraperService
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()
security = HTTPBearer()
API_TOKEN = os.getenv("API_TOKEN")
CACHE_HOST = os.getenv("CACHE_HOST")
CACHE_PORT = os.getenv("CACHE_PORT")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # if credentials.credentials != "secure_static_token_123456":
    print("ENV CREDENTIALS........",API_TOKEN,"CACHE HOST",CACHE_HOST,"CACHE PORT",CACHE_PORT)
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )

@router.post("/scrape", dependencies=[Depends(verify_token)])
async def scrape_products(settings: ScraperSettings):
    try:
        # Log environment variables to the console
        print(f"API_TOKEN: {API_TOKEN}")
        print(f"CACHE_HOST: {CACHE_HOST}")
        print(f"CACHE_PORT: {CACHE_PORT}")

        image_directory = "./image_directory"
        scraper_service = ScraperService(image_directory=image_directory, settings=settings)
    
        await scraper_service.scrape()
        return {"message": "Scraping completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/cache")
async def get_cache():
    scraper_service = ScraperService(image_directory="./image_directory", settings=ScraperSettings(num_pages=1))
    return scraper_service.get_cache()