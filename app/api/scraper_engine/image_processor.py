import requests
from PIL import Image
from io import BytesIO
from xml.etree import ElementTree
import cairosvg
from urllib.parse import urlparse
from typing import Tuple
from pydantic import BaseModel, Field
import base64


class ImageProcessorMetaData(BaseModel):
    url: str = Field(..., title="Url of the image")
    img_base64: str = Field(..., title="Base64 encoded image")
    size: Tuple[int, int] = Field(..., title="Size of the image")


class ImageProcessor:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def correct_relative_url(self, base_url: str, url: str) -> str:
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = base_url + url
        elif not urlparse(url).scheme:
            url = base_url + "/" + url
        return url

    async def get_image_size(self, url: str) -> ImageProcessorMetaData:
        url = self.correct_relative_url(self.base_url, url)
        if url.endswith(".svg"):
            image_base64, size = await self.get_svg_data(url)
        else:
            image_base64, size = await self.get_raster_image_data(url)
        return ImageProcessorMetaData(url=url, img_base64=image_base64, size=size)

    async def get_raster_image_data(self, url: str) -> Tuple[str, Tuple[int, int]]:
        try:

            response = requests.get(url, allow_redirects=True).content
            with Image.open(BytesIO(response)) as img:
                size = img.size
                buffered = BytesIO()
                img.save(buffered, format=img.format)
                img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                return (img_base64, size)

        except Exception as e:
            print(f"Could not retrieve image from {url}: {e}")
            return ("", (0, 0))

    async def get_svg_data(self, url: str) -> Tuple[str, Tuple[int, int]]:
        try:
            svg_data = requests.get(url, allow_redirects=True).content
            svg = ElementTree.fromstring(svg_data)
            width = svg.get("width", "").replace("px", "")
            height = svg.get("height", "").replace("px", "")

            if width.isdigit() and height.isdigit():
                size = (int(width), int(height))
            else:
                png_data = cairosvg.svg2png(bytestring=svg_data)
                if not png_data:
                    raise ValueError("Could not convert SVG to PNG")
                with Image.open(BytesIO(png_data)) as img:
                    size = img.size
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    png_data = buffered.getvalue()

            img_base64 = base64.b64encode(png_data).decode("utf-8")
            return (img_base64, size)

        except Exception as e:
            print(f"Could not retrieve SVG image info for {url}: {e}")
            return ("", (0, 0))
