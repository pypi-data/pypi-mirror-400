from .html_nested_base_handler import get_element_content as get_element_content
from gllm_docproc.loader.html.exception import HtmlLoadException as HtmlLoadException
from gllm_docproc.loader.html.html_base_loader import HTMLBaseLoader as HTMLBaseLoader
from gllm_docproc.loader.html.utils.html_utils import extract_html_head as extract_html_head
from gllm_docproc.loader.html.utils.removed_components import RemovedComponents as RemovedComponents
from gllm_docproc.utils.html_constants import ContentDataKeys as ContentDataKeys, MetaDataKeys as MetaDataKeys

class HTMLNestedLoader(HTMLBaseLoader):
    """A loader class for loading web content and extracting information.

    This class inherits from the BaseLoader class and provides methods to load web content,
    extract information, and scrape data using Scrapy spiders.
    """
    def __init__(self) -> None:
        """Initialize the HTMLNestedLoader."""
