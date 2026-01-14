from _typeshed import Incomplete
from gllm_docproc.downloader.base_downloader import BaseDownloader as BaseDownloader
from gllm_docproc.downloader.html.utils.web_utils import generate_filename_from_url as generate_filename_from_url
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, HTML as HTML
from gllm_docproc.utils.file_utils import save_to_json as save_to_json
from typing import Any

class HTMLFirecrawlDownloader(BaseDownloader):
    """A downloader class for downloading web content using Firecrawl.

    This class inherits from the BaseDownloader class and provides methods to download web content using Firecrawl.

    Attributes:
        firecrawl_instance (FirecrawlApp): The Firecrawl instance.
    """
    logger: Incomplete
    firecrawl_instance: Incomplete
    def __init__(self, api_key: str, api_url: str | None = None) -> None:
        """Initialize the Firecrawl downloader.

        Args:
            api_key (str): The API key for Firecrawl.
            api_url (str, optional): The API URL for Firecrawl.
        """
    def download(self, source: str, output: str, **kwargs: Any) -> list[str]:
        """Download content and save to file as JSON.

        Args:
            source (str): The URL to scrape.
            output (str): The directory path where the downloaded content (in JSON format) will be saved.
            **kwargs (Any): Additional arguments to pass to the scraper.

        Kwargs:
            formats (list[str], optional): The formats to scrape. Supported formats include:
                - markdown: Returns the markdown content of the page.
                - html: Returns the processed HTML content of the page.
                - rawHtml: Provides the unmodified, raw HTML content of the entire webpage.
                - screenshot: Returns a screenshot of the page.
                - screenshot@fullPage: Returns a screenshot of the full page.
                - links: Extracts and returns a list of all links found on the scraped page.
                - json: Allows for structured data extraction, Need to use `json_options` to define
                        the schema for the output.

                For a comprehensive list of supported formats, refer to the Firecrawl documentation.
                Defaults to ['html'].

        Returns:
            list[str]: The list of full filepath of the created JSON files.
        """
