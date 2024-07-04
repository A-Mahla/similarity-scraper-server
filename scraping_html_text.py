from bs4 import BeautifulSoup, Tag, NavigableString, PageElement
from anytree import NodeMixin
from typing import Optional, Union, Tuple
import requests
from pydantic import HttpUrl, BaseModel, Field
from langdetect import detect
from PIL import Image
from io import BytesIO
from xml.etree import ElementTree
import cairosvg
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

    def __init__(self, url: HttpUrl, is_image: bool = False):
        self.website = Website(url=url)
        self.img_proc = ImageProcessor(self.website.base_url)
        response = requests.get(str(self.website.url))
        if response.status_code != 200:
            return None
        self.soup = BeautifulSoup(response.content, "html.parser")
        self.is_image = is_image
        self.root, self.best_node = self.build_tree(self.soup)

    def build_tree(
        self,
        element: Union[Tag, NavigableString],
        parent: Optional[Node] = None,
        depth: int = 0,
        best_node: Optional[Node] = None,
    ) -> Tuple[Node, Node]:
        node_name = (
            element.name if isinstance(element, Tag) and element.name else "text"
        )
        node = Node(
            node_name,
            data=element,
            breadth=len(list(element.children)) if isinstance(element, Tag) else 1,
            parent=parent,
        )
        node.score = (
            self.image_score(node)
            if self.is_image
            else self.text_score(node, node_name)
        )

        if best_node is None or node.score > best_node.score:
            best_node = node

        if isinstance(element, Tag):
            for child in element.children:
                if isinstance(child, Tag) or (
                    isinstance(child, NavigableString) and child.strip()
                ):
                    _, best_child = self.build_tree(
                        child, parent=node, depth=depth + 1, best_node=best_node
                    )
                    if best_child.score > best_node.score:
                        best_node = best_child

        return node, best_node

    def is_english(self, text: str) -> bool:
        try:
            return detect(text) == "en"
        except Exception:
            return False

    def calculate_text_density(self, node: Node) -> int:
        text = node.data.get_text(strip=True) if node.data else ""
        return len(text) if self.is_english(text) else 0

    def text_score(self, node: Node, node_name: str) -> int:
        if node_name not in ScraperGraph.relevant_text_tags:
            return 0
        node.text_density = self.calculate_text_density(node)
        return node.depth * node.breadth * node.text_density

    def image_score(self, node: Node) -> float:
        if isinstance(node.data, Tag) and node.name == "img":
            alt_text = node.data.get("alt", "")
            alt_text_density = len(alt_text) if isinstance(alt_text, str) else 1
            src = node.data.get("src", "")
            width, height = (
                self.img_proc.get_image_size(src) if isinstance(src, str) else (0, 0)
            )
            size_score = width * height
            return (alt_text_density + size_score) / (node.depth + 1)
        else:
            return 0

    def get_best_node(self) -> Node:
        return self.best_node


if __name__ == "__main__":
    image = True
    tree = ScraperGraph("https://en.wikipedia.org/wiki/Dick_Schoof", is_image=image)
    best_node = tree.get_best_node()
    print(f"Best node tag: {best_node.name}")
    if not image:
        print(f"Best node content: {best_node.data.get_text(strip=True)}")
    else:
        print(f"Best node content: {best_node.data}")
