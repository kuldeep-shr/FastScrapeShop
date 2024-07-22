from pydantic import BaseModel

class ScraperSettings(BaseModel):
    num_pages: int
