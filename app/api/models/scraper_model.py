from pydantic import BaseModel, Field
from typing import Literal
from scraper.language_supported import LanguageSupported


class ScraperResponse(BaseModel):
    content: str = Field(..., title="Content of the tag")
    language: LanguageSupported = Field(..., title="Language of the content")
    tag: str = Field(..., title="Html/XSS Tag")
    status: Literal["success", "failed"] = Field(
        "success", title="Status of the request"
    )
    message: str = Field(
        "Text content was successfully extracted from the page.", title="status message"
    )
