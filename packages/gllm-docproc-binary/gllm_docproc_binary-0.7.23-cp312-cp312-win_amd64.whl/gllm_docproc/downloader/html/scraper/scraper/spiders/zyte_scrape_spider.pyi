from .scrape_spider import ScrapeSpider as ScrapeSpider
from _typeshed import Incomplete
from collections.abc import Generator
from scrapy.crawler import Crawler
from scrapy.http import Response
from typing import Any

class ZyteScrapeSpider(ScrapeSpider):
    """A Scrapy spider designed to scrape content from a website using the Zyte API.

    This spider is specifically tailored for scraping content from a website using the Zyte API to handle block and
    render Javascript loaded page.

    Attributes:
        name (str): The name of the spider - 'zyte_scrape_spider'.
        allowed_domains (list): The list of allowed domains for crawling.
        start_urls (list): The starting URLs for the spider to initiate crawling
        custom_settings (dict): Custom settings for the spider, including item pipelines configuration.
    """
    name: str
    custom_settings: dict[str, Any]
    @classmethod
    def from_crawler(cls, crawler: Crawler, *args: Any, **kwargs: Any):
        """Create an instance of the spider from a Scrapy crawler.

        This method is a class method that is called by Scrapy to create an instance of the spider
        based on the provided Scrapy crawler and additional arguments.

        Args:
            crawler: The Scrapy crawler object.
            *args: Variable length argument list.
            **kwargs: Variable length keyword argument list.

        Returns:
            WebLoaderSpider: An instance of the spider.
        """
    async def start(self) -> Generator[Incomplete]:
        """Start Request.

        Initiates requests for the specified start URLs using Scrapy requests with additional
        meta information for zyte usage.

        This method iterates over the start_urls list and creates a Scrapy Request for each URL.
        The Request includes meta information to enable the browserHtml feature of the Zyte Automatic Extraction API.
        """
    def parse(self, response: Response) -> None:
        """Parses the HTML response obtained from the website.

        Args:
            response (scrapy.http.Response): The response object to parse.
        """
