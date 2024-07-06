from bs4 import BeautifulSoup, Tag, NavigableString
from anytree import NodeMixin
from typing import Optional, Union, Tuple
import httpx
from pydantic import HttpUrl
from langdetect import detect
from scraper_engine.image_processor import ImageProcessor, ImageProcessorMetaData
from scraper_engine.website import Website
from scraper_engine.language_supported import LanguageSupported


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
        self.img_metadata: Optional[ImageProcessorMetaData] = None


class ScraperGraph:

    language: LanguageSupported
    website: Website
    img_proc: ImageProcessor
    soup: BeautifulSoup
    image_search: bool
    root: Node
    best_node: Node

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

    class NoFound(ValueError):
        pass

    @classmethod
    async def create(
        cls,
        url: HttpUrl,
        image_search: bool = False,
        language: LanguageSupported = LanguageSupported.EN,
    ):

        async with httpx.AsyncClient() as client:
            response = await client.get(str(url))
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch the website: {url}")
            soup = BeautifulSoup(response.content, "html.parser")

        instance = cls.__new__(cls)
        instance.language = language
        instance.website = Website(url=url)
        instance.img_proc = ImageProcessor(instance.website.base_url)
        instance.image_search = image_search
        instance.soup = soup
        instance.root, instance.best_node = await instance.build_tree(soup)
        return instance

    async def build_tree(
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
            await self.image_score(node)
            if self.image_search
            else self.text_score(node, node_name)
        )

        if best_node is None or node.score > best_node.score:
            best_node = node

        if isinstance(element, Tag):
            for child in element.children:
                if isinstance(child, Tag) or (
                    isinstance(child, NavigableString) and child.strip()
                ):
                    _, best_child = await self.build_tree(
                        child, parent=node, depth=depth + 1, best_node=best_node
                    )
                    if best_child.score > best_node.score:
                        best_node = best_child

        return node, best_node

    def is_language(self, text: str) -> bool:
        try:
            return detect(text) == self.language.value  # default is "en" for English
        except Exception:
            return False

    def calculate_text_density(self, node: Node) -> int:
        text = node.data.get_text(" ", strip=True) if node.data else ""
        return len(text) if self.is_language(text) else -1

    def text_score(self, node: Node, node_name: str) -> int:
        if node_name not in ScraperGraph.relevant_text_tags:
            return -1
        node.text_density = self.calculate_text_density(node)
        if node.text_density <= 0:
            return -1  # not in the desired language or empty
        return node.depth * node.breadth * node.text_density

    async def image_score(self, node: Node) -> float:
        if isinstance(node.data, Tag) and node.name == "img":
            alt_text = node.data.get("alt", "")
            alt_text_density = len(alt_text) if isinstance(alt_text, str) else 1
            src = node.data.get("src", "")
            if not src or not isinstance(src, str):
                return -1.0
            metadata = await self.img_proc.get_image_size(src)
            size_score = metadata.size[0] * metadata.size[1]  # height * width
            if size_score == 0:
                return -1.0
            node.img_metadata = metadata
            return (alt_text_density + size_score) / (node.depth + 1)
        else:
            return -1.0

    def get_best_node(self) -> Node:
        if self.image_search and self.best_node.score < 0:
            raise ScraperGraph.NoFound(
                f"No image found on the webpage (url: {self.website.url}).\n"
                "Only 'img' tag is considered.\n"
                "Other tags are ignored."
            )
        elif self.best_node.score < 0:
            raise ScraperGraph.NoFound(
                f"No language type '{self.language.value}' found on the webpage (url: {self.website.url}).\n"
                f"Only html tags ({', '.join([t for t in ScraperGraph.relevant_text_tags])}) are considered.\n"
                "Other tags are ignored."
            )
        else:
            return self.best_node
