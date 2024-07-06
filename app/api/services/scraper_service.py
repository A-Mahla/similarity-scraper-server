from fastapi import HTTPException
from models.scraper_model import ScraperResponse, ScraperMetaData, ScraperType
from models.sample_model import Sample
from scraper_engine.scraper_graph import ScraperGraph
from scraper_engine.language_supported import LanguageSupported
from services.sample_service import SampleService
from pydantic import HttpUrl
import traceback
import logging


logger = logging.getLogger("uvicorn")


class ScraperService:

    @staticmethod
    async def scraper_search(
        url: HttpUrl,
        image_search: bool,
        language: LanguageSupported = LanguageSupported.EN,
    ) -> ScraperMetaData:

        tree = await ScraperGraph.create(
            url, image_search=image_search, language=language
        )
        best_node = tree.get_best_node()
        content = (
            best_node.img_metadata.img_base64
            if best_node.img_metadata
            else best_node.data.get_text(strip=True)
        )
        return ScraperMetaData(
            url=url,
            content=content,
            image_url=(best_node.img_metadata.url if best_node.img_metadata else None),
            tag=best_node.name,
            language=language,
            type=ScraperType.IMAGE if image_search else ScraperType.TEXT,
        )

    @staticmethod
    async def get_best_page_text(
        url: HttpUrl,
        image_search: bool,
        language: LanguageSupported = LanguageSupported.EN,
    ) -> ScraperResponse:

        try:
            metadata = await ScraperService.scraper_search(
                url=url, image_search=image_search, language=language
            )
            sample = await SampleService.add_sample(Sample(metadata=metadata))
            return ScraperResponse(
                metadata=metadata,
                status="success",
                message=f"{'Image' if image_search else 'Text'} content was successfully extracted from the page.",
                database_log=sample.message,
            )

        except ScraperGraph.NoFound as e:
            return ScraperResponse(
                metadata=ScraperMetaData(
                    url=url,
                    content="None",
                    tag="None",
                    language=language,
                    type=ScraperType.IMAGE if image_search else ScraperType.TEXT,
                ),
                status="failed",
                message=f"{e}",
                database_log="",
            )

        except Exception:
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Failed to scrape the webpage")
