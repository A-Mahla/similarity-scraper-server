from bs4 import BeautifulSoup, Tag, NavigableString
from anytree import NodeMixin
from typing import Optional, Union, Tuple
import requests
from pydantic import HttpUrl
from langdetect import detect
from scraper.image_processor import ImageProcessor
from scraper.website import Website
from scraper.language_supported import LanguageSupported


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

    class LanguageNoFound(ValueError):
        pass

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

    def __init__(
        self,
        url: HttpUrl,
        image_search: bool = False,
        language: LanguageSupported = LanguageSupported.EN,
    ):
        self.language = language
        self.website = Website(url=url)
        self.img_proc = ImageProcessor(self.website.base_url)
        response = requests.get(str(self.website.url))
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch the website: {self.website.url}")
        self.soup = BeautifulSoup(response.content, "html.parser")
        self.image_search = image_search
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
                    _, best_child = self.build_tree(
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
        text = node.data.get_text(strip=True) if node.data else ""
        if len(text) == 0:
            return 0
        return len(text) if self.is_language(text) else -1

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
        if self.best_node.score < 0:
            raise ScraperGraph.LanguageNoFound(
                f"No language type '{self.language.value}' found on the webpage"
            )
        else:
            return self.best_node


if __name__ == "__main__":
    image = True
    tree = ScraperGraph("https://en.wikipedia.org/wiki/Dick_Schoof", image_search=image)
    best_node = tree.get_best_node()
    print(f"Best node tag: {best_node.name}")
    if not image:
        print(f"Best node content: {best_node.data.get_text(strip=True)}")
    else:
        print(f"Best node content: {best_node.data}")
