from pydantic import HttpUrl, BaseModel, Field
from urllib.parse import urlparse, urlunparse


class Website(BaseModel):
    url: HttpUrl = Field(
        ...,
        description="The URL of the website to scrape.",
    )

    @property
    def base_url(self) -> str:
        """Compute and return the base URL from the full URL."""
        parsed_url = urlparse(str(self.url))
        return urlunparse((parsed_url.scheme, parsed_url.netloc, "", "", "", ""))
