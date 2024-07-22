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
PROXY = os.getenv("PROXY")  # Load proxy from environment variables

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )

@router.post("/scrape", dependencies=[Depends(verify_token)])
async def scrape_products(settings: ScraperSettings):
    try:
        image_directory = "./image_directory"
        
        # Pass the proxy string to the ScraperService
        scraper_service = ScraperService(image_directory=image_directory, settings=settings, proxy=PROXY)
    
        await scraper_service.scrape()
        return {"message": "Scraping completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
