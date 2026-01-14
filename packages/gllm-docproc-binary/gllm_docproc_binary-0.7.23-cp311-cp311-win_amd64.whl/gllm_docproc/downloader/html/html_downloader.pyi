from _typeshed import Incomplete
from gllm_docproc.downloader.base_downloader import BaseDownloader as BaseDownloader
from gllm_docproc.downloader.html.exception import ItemScrapeFailedException as ItemScrapeFailedException
from gllm_docproc.downloader.html.scraper.scraper.spiders import CrawlBaseSpider as CrawlBaseSpider, CrawlSitemapLinkSpider as CrawlSitemapLinkSpider, CrawlSitemapSpider as CrawlSitemapSpider
from gllm_docproc.downloader.html.scraper.web_scraper_executor import WebScraperExecutor as WebScraperExecutor
from gllm_docproc.downloader.html.utils import generate_filename_from_url as generate_filename_from_url, is_valid_url as is_valid_url
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, HTML as HTML
from gllm_docproc.utils.file_utils import create_full_path as create_full_path, save_file as save_file, save_to_json as save_to_json
from scrapy import Spider as Spider
from typing import Any

class HTMLDownloader(BaseDownloader):
    """A downloader class for downloading web content.

    This class inherits from the BaseDownloader class and provides methods to download web content.

    Args:
        **kwargs (Any): Additional keyword arguments.
    """
    URL_INDEX: int
    CONTENT_INDEX: int
    kwargs: Incomplete
    logger: Incomplete
    def __init__(self, **kwargs: Any) -> None:
        """Initializes the WebDownloader class.

        Args:
            **kwargs (Any): Additional keyword arguments.
        """
    def download(self, source: str, output: str, **kwargs: Any) -> list[str]:
        """Downloads and saves web content from a single URL.

        This method uses a web scraper to fetch the HTML content from the specified URL
        and saves it as a JSON file in the given output directory.

        Args:
            source (str): The URL of the web content to download.
            output (str): The directory path where the downloaded content (in JSON format) will be saved.
            **kwargs (Any): Additional keyword arguments.

        Kwargs:
            include_markdown (bool, optional): Whether to include markdown conversion in the output. Defaults to False.

        Returns:
            list[str]: The list of full filepath of the created JSON files.

        Raises:
            ItemScrapeFailedException: If the provided source is not a valid URL, or if the web content
                cannot be successfully scraped or downloaded from the URL.
        """
    def download_from_multiple_urls(self, urls: list[str], output: str = '.', **kwargs: Any) -> list[str]:
        """Downloads web content from multiple URLs.

        Args:
            urls (list[str]): The URLs to download.
            output (str): The output where we put the downloaded content (usually a folder path).
            **kwargs (Any): Additional keyword arguments.

        Kwargs:
            include_markdown (bool, optional): Whether to include markdown conversion in the output. Defaults to False.

        Returns:
            list[str]: The list of full filepath of the created JSON files.
        """
    def download_crawl(self, urls: list[str] | str, output: str = '.', spider_type: type[Spider] | None = None, **kwargs: Any) -> list[str]:
        """Downloads web content from the provided URLs.

        This method uses a web scraper to crawl the provided URLs and saves the downloaded content to a file.

        Args:
            output (str): The output where we put the downloaded content (usually a folder path).
            urls (list[str] | str): The URLs to crawl. Can be a single URL (str) or a list of URLs (list[str]).
            spider_type (type[Spider] | None): The type of spider to use for downloading.
                Defaults to None, which will use CrawlBaseSpider.
            **kwargs (Any): Additional keyword arguments.

        Kwargs:
            include_markdown (bool, optional): Whether to include markdown conversion in the output. Defaults to False.

        Returns:
            list[str]: The list of full filepath of the created JSON files.
        """
    def download_sitemap(self, urls: list[str] | str, output: str = '.', spider_type: type[Spider] | None = None, **kwargs: Any) -> list[str]:
        """Downloads web content from the sitemap of the provided URLs.

        This method uses a web scraper to scrape the sitemap of each URL and saves the downloaded content to a file.

        Args:
            urls (list[str] | str): The URLs to scrape. Can be a single URL (str) or a list of URLs (list[str]).
            output (str): The output where we put the downloaded content (usually a folder path).
            spider_type (type[Spider] | None): The type of spider to use for downloading.
                Defaults to None, which will use CrawlSitemapSpider.
            **kwargs (Any): Additional keyword arguments.

        Kwargs:
            include_markdown (bool, optional): Whether to include markdown conversion in the output. Defaults to False.

        Returns:
            list[str]: The list of full filepath of the created JSON files.
        """
    def download_sitemap_links(self, urls: list[str] | str, output: str = '.', spider_type: type[Spider] | None = None) -> None:
        """Retrieves all links from the sitemap of the provided URLs.

        This method uses a web scraper to scrape the sitemap of each URL and returns a list of all found links.

        Args:
            urls (list[str] | str): The URLs to scrape. Can be a single URL (str) or a list of URLs (list[str]).
            output (str): The output where we put the downloaded content (usually a folder path).
            spider_type (type[Spider] | None)): The type of spider to use for downloading.
                Defaults to None, which will use CrawlSitemapLinkSpider.

        Returns:
            None
        """
