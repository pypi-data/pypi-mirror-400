from _typeshed import Incomplete
from collections.abc import Generator
from scrapy.crawler import Crawler
from scrapy.http import Request, Response
from scrapy.spiders import CrawlSpider
from typing import Any

class CrawlBaseSpider(CrawlSpider):
    """A Scrapy CrawlSpider designed to crawl and extract content from website.

    Attributes:
        name (str): The name of the spider - 'crawl_spider'.
        allowed_domains (list): The allowed domains for spider to crawl.
        start_urls (list): The starting URLs for the spider to initiate crawling.
        custom_settings (dict): Custom settings for the spider, including item pipelines configuration.
        rules (tuple): The rules to be followed during the crawling process.
    """
    name: str
    rules: Incomplete
    custom_settings: dict[str, Any]
    start_urls: Incomplete
    allowed_domains: Incomplete
    callback: Incomplete
    removed_components: Incomplete
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the CrawlBaseSpider."""
    def add_playwright(self, request: Request, _: Response):
        """Adds playwright meta information to the request."""
    async def start(self) -> Generator[Incomplete]:
        """Start Request.

        Initiates requests for the specified start URLs using Scrapy requests with additional
        meta information for playwright usage.
        """
    def parse_web(self, response: Response):
        """Parses the response obtained from the website, distinguishing between HTML content and other file types.

        Args:
            response (Response): The response object containing the page content.

        Returns:
            None
        """
    def follow_selected_urls(self, response: Response):
        """Follows selected URLs from the response.

        Args:
            response (Response): The response object containing the page content.

        Returns:
            None
        """
    @classmethod
    def from_crawler(cls, crawler: Crawler, *args: Any, **kwargs: Any):
        """Creates a new instance of the CrawlBaseSpider with custom settings.

        Args:
            crawler (Crawler): The crawler object.
            *args (Any): The arguments to be passed to the spider.
            **kwargs (Any): The keyword arguments to be passed to the spider.

        Returns:
            CrawlBaseSpider: The CrawlBaseSpider instance.
        """
    async def errback(self, failure: Any):
        """Handles errors encountered during the crawling process and closes playwright pages."""
