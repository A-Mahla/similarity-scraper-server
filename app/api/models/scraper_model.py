from pydantic import BaseModel, Field, HttpUrl
from typing import Literal, Optional
from enum import Enum
from scraper_engine.language_supported import LanguageSupported


class ScraperType(str, Enum):
    TEXT = "text"
    IMAGE = "image"


class ScraperMetaData(BaseModel):
    url: HttpUrl = Field(..., title="Url of the page")
    image_url: Optional[str] = Field(default=None, title="Url of the image")
    tag: str = Field(..., title="Html/XSS Tag")
    language: LanguageSupported = Field(..., title="Language of the content")
    type: ScraperType = Field(..., title="Type of the content")
    content: str = Field(..., title="Text or Image (base 64) of the page")


class ScraperResponse(BaseModel):
    metadata: ScraperMetaData = Field(..., title="Metadata of the content")
    status: Literal["success", "failed"] = Field(
        "success", title="Status of the request"
    )
    message: str = Field(
        "Text content was successfully extracted from the page.", title="status message"
    )
    database_log: str = Field(..., title="Database message")
