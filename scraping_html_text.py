from bs4 import BeautifulSoup, Tag, NavigableString
from anytree import NodeMixin
from typing import Optional, Union
import requests
from pydantic import HttpUrl, BaseModel
from langdetect import detect
from PIL import Image
from io import BytesIO
from xml.etree import ElementTree
import cairosvg
from urllib.parse import urlparse, urlunparse


class Website(BaseModel):
    url: HttpUrl
    base_url: str


class ImageProcessor:
    def __init__(self, base_url):
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
            response = requests.get(url)
            with Image.open(BytesIO(response.content)) as img:
                return img.size  # (width, height)
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


class Node(NodeMixin):
    def __init__(
        self,
        name: str,
        data: Union[Tag, NavigableString],
        breadth: int,
        parent: Optional["Node"] = None,
    ):
        self.name = name
        self.parent = parent
        self.data = data
        self.breadth = breadth
        self.text_density = 0
        self.tag_weight = 0
        self.score: Union[int, float] = 0


class ScraperGraph:

    relevant_text_tags = [
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "article",
        "section",
        "p",
        "blockquote",
        "li",
        "td",
        "th",
    ]

    @staticmethod
    def get_base_url(url: HttpUrl) -> str:
        """Extract the base URL from a full URL."""
        parsed_url = urlparse(str(url))
        base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, "", "", "", ""))
        return base_url

    def __init__(self, url: HttpUrl, is_image: bool = False):
        self.website = Website(url=url, base_url=ScraperGraph.get_base_url(url))
        response = requests.get(str(self.website.url))
        if response.status_code != 200:
            return None
        self.soup = BeautifulSoup(response.content, "html.parser")
        self.is_image = is_image
        self.root = self.build_tree(self.soup)

    def build_tree(
        self,
        element: Union[Tag, NavigableString],
        parent: Optional[Node] = None,
        depth: int = 0,
    ) -> Node:
        node_name = (
            element.name if isinstance(element, Tag) and element.name else "text"
        )
        node = Node(
            node_name,
            data=element,
            breadth=len([element.children]) if isinstance(element, Tag) else 1,
            parent=parent,
        )
        node.score = (
            self.image_score(node)
            if self.is_image
            else self.text_score(node, node_name)
        )
        # node.score = node.depth * node.breadth * node.text_density * node.tag_weight

        if isinstance(element, Tag):
            for child in element.children:
                if isinstance(child, Tag) or (
                    isinstance(child, NavigableString) and child.strip()
                ):
                    self.build_tree(child, parent=node, depth=depth + 1)
        return node

    def is_english(self, text: str) -> bool:
        try:
            return detect(text) == "en"
        except Exception:
            return False

    def calculate_text_density(self, node: Node) -> int:
        if not node.children:
            text = node.data.get_text(strip=True) if node.data else ""
            return len(text) if self.is_english(text) else 0
        return sum(self.calculate_text_density(child) for child in node.children)

    def text_score(self, node: Node, node_name: str) -> int:
        node.text_density = self.calculate_text_density(node)
        node.tag_weight = 1 if node_name in ScraperGraph.relevant_text_tags else 0
        return node.depth * node.breadth * node.text_density * node.tag_weight

    def correct_relative_url(self, base_url: str, relative_url: str) -> str:
        """Correct relative URLs using the base URL."""
        if relative_url.startswith("//"):
            return f"{base_url.split(':')[0]}:{relative_url}"
        elif relative_url.startswith("/"):
            return f"{base_url}{relative_url}"
        elif not urlparse(relative_url).netloc:
            return f"{base_url}/{relative_url}"
        else:
            return relative_url

    def get_image_size(self, url: str):
        try:
            url = self.correct_relative_url(self.website.base_url, url)
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            return img.size
        except Exception as e:
            print(f"Could not retrieve image size for {url}: {e}")
            return (0, 0)

    def image_score(self, node: Node) -> float:
        if isinstance(node.data, Tag) and node.name == "img":
            alt_text = node.data.get("alt", "")
            alt_text_density = len(alt_text) if isinstance(alt_text, str) else 1
            src = node.data.get("src", "")
            img_proc = ImageProcessor(self.website.base_url)
            width, height = (
                img_proc.get_image_size(src) if isinstance(src, str) else (0, 0)
            )
            size_score = width * height
            return (alt_text_density + size_score) / (node.depth + 1)
        else:
            return 0

    def find_best_node(self, node: Node) -> Node:
        best_node = node
        for child in node.children:
            candidate = self.find_best_node(child)
            if candidate.score > best_node.score:
                best_node = candidate
        return best_node


if __name__ == "__main__":
    image = False
    tree = ScraperGraph("https://www.hcompany.ai/", is_image=image)
    best_node = tree.find_best_node(tree.root)
    print(f"Best node tag: {best_node.name}")
    if not image:
        print(f"Best node content: {best_node.data.get_text(strip=True)}")
    else:
        print(f"Best node content: {best_node.data}")
