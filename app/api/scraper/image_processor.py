import requests
from PIL import Image
from io import BytesIO
from xml.etree import ElementTree
import cairosvg
from urllib.parse import urlparse


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

    def get_image_size(self, url: str):
        url = self.correct_relative_url(self.base_url, url)
        if url.endswith(".svg"):
            return self.get_svg_size(url)
        else:
            return self.get_raster_image_size(url)

    def get_raster_image_size(self, url: str):
        try:
            response = requests.get(url, allow_redirects=True)
            with Image.open(BytesIO(response.content)) as img:
                return img.size
        except Exception as e:
            print(f"Could not retrieve raster image size for {url}: {e}")
            return (0, 0)

    def get_svg_size(self, url: str):
        try:
            svg_data = requests.get(url).content
            svg = ElementTree.fromstring(svg_data)
            width = svg.get("width", "").replace("px", "")
            height = svg.get("height", "").replace("px", "")
            if width.isdigit() and height.isdigit():
                return (int(width), int(height))
            else:
                png_data = cairosvg.svg2png(bytestring=svg_data)
                if not png_data:
                    raise ValueError("Could not convert SVG to PNG")
                with Image.open(BytesIO(png_data)) as img:
                    return img.size
        except Exception as e:
            print(f"Could not retrieve SVG image size for {url}: {e}")
            return (0, 0)
