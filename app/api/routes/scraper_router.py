from fastapi import APIRouter, status, Body, Query
from pydantic import HttpUrl
from models.scraper_model import ScraperResponse
from services.scraper_service import ScraperService
from scraper.language_supported import LanguageSupported
import logging


router = APIRouter()
logger = logging.getLogger("uvicorn")


# curl -X POST "http://yourdomain.com/scraper/" \
#      -H "Content-Type: application/json" \
#      -d '{
#          "url": "https://www.hcompany.ai/",
#          "image_search": false,
#     }'
@router.post(
    "/",
    response_description="Scrape a webpage to get the best text",
    status_code=status.HTTP_201_CREATED,
    response_model=ScraperResponse,
)
def scrape_page(
    url: HttpUrl = Body(...),
    image_search: bool = Body(default=False),
    language: LanguageSupported = Body(default=LanguageSupported.EN),
) -> ScraperResponse:
    logger.info(f"Scraping page: {url}")
    return ScraperService.get_best_page_text(url, image_search, language)
