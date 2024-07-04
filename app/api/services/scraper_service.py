from fastapi import HTTPException
from models.scraper_model import ScraperResponse
from scraper.scraper_graph import ScraperGraph
from scraper.language_supported import LanguageSupported
from pydantic import HttpUrl
from bs4 import NavigableString
import logging


logger = logging.getLogger("uvicorn")


class ScraperService:

    @staticmethod
    def get_best_page_text(
        url: HttpUrl,
        image_search: bool,
        language: LanguageSupported = LanguageSupported.EN,
    ) -> ScraperResponse:
        try:
            tree = ScraperGraph(url, image_search=image_search, language=language)
            best_node = tree.get_best_node()
            content = (
                best_node.data.get("src", "")
                if image_search and not isinstance(best_node.data, NavigableString)
                else best_node.data.get_text(strip=True)
            )
            return ScraperResponse(
                tag=best_node.name,
                content=content,  # type: ignore
                language=language,
                status="success",
                message=f"{'Image' if image_search else 'Text'} content was successfully extracted from the page.",
            )
        except ScraperGraph.LanguageNoFound as e:
            return ScraperResponse(
                tag="None",
                content="None",
                language=language,
                status="failed",
                message=f"{e}",
            )
        except Exception as e:
            logger.error(f"Failed to scrape the webpage: {e}")
            raise HTTPException(status_code=500, detail="Failed to scrape the webpage")
