from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.html.utils.html_utils import is_html_content as is_html_content
from typing import Any

class HTMLBaseLoader(BaseLoader):
    """A loader class for loading web content and extracting information.

    This class inherits from the BaseLoader class and provides methods to load web content,
    extract information, and scrape data using Scrapy spiders.
    """
    URL_INDEX: int
    CONTENT_INDEX: int
    def __init__(self, load_from_html_string: Any) -> None:
        """Initialize the HTMLBaseLoader."""
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Loads web content and returns the extracted information in JSON format.

        Args:
            source (str): The source of the web content, either a URL or a file path.
            loaded_elements (list[dict]): A list of loaded elements to be processed.
            **kwargs (dict[str, Any]): Additional keyword arguments.

        Returns:
            list[dict]: The extracted information in JSON format.
        """
