from fastapi import FastAPI
from app.controllers.scraper_controller import router as scraper_router
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Debug prints to ensure the environment variables are loaded
print(f"API_TOKEN: {os.getenv('API_TOKEN')}")
print(f"CACHE_HOST: {os.getenv('CACHE_HOST')}")
print(f"CACHE_PORT: {os.getenv('CACHE_PORT')}")

app = FastAPI()

# Include the scraper routes
app.include_router(scraper_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)