from gllm_docproc.loader.html.exception import HtmlLoadException as HtmlLoadException
from gllm_docproc.loader.html.flat.html_flat_base_handler import handle_base_element as handle_base_element, is_base_element as is_base_element
from gllm_docproc.loader.html.flat.html_flat_merger import merge_html_elements as merge_html_elements
from gllm_docproc.loader.html.html_base_loader import HTMLBaseLoader as HTMLBaseLoader
from gllm_docproc.loader.html.utils.html_utils import extract_html_head as extract_html_head, extract_html_title_tag as extract_html_title_tag
from gllm_docproc.loader.html.utils.removed_components import RemovedComponents as RemovedComponents
from gllm_docproc.model.element import Element as Element
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata
from parsel import Selector, SelectorList

class HTMLFlatLoader(HTMLBaseLoader):
    """A loader class for loading web content and extracting information.

    This class inherits from the BaseLoader class and provides methods to load web content,
    extract information, and scrape data using Scrapy spiders.
    """
    def __init__(self) -> None:
        """Initialize the HTMLFlatLoader."""
    @classmethod
    def extract_html_element(cls, content_selector: SelectorList[Selector] | Selector, html_head: ElementMetadata, removed_components: RemovedComponents) -> list[Element]:
        """Recursively extract the content of an HTML element.

        Args:
            content_selector (SelectorList[Selector] | Selector): The content selector.
            html_head (ElementMetadata): The HTML head metadata.
            removed_components (RemovedComponents): The removed components.

        Returns:
                list[Element]: A list of web elements.
        """
