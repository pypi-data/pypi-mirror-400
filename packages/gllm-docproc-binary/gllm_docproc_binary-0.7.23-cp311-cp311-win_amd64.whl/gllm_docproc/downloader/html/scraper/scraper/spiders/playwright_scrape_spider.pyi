from .scrape_spider import ScrapeSpider as ScrapeSpider
from _typeshed import Incomplete
from collections.abc import Generator
from typing import Any

class PlaywrightScrapeSpider(ScrapeSpider):
    """A Scrapy spider designed to scrape content from website using playwright to render Javascript loaded page.

    Attributes:
        name (str): The name of the spider - 'playwright_scrape_spider'.
        allowed_domains (list): The allowed domains for spider to crawl.
        start_urls (list): The starting URLs for the spider to initiate crawling
        custom_settings (dict): Custom settings for the spider, including item pipelines configuration.
    """
    name: str
    custom_settings: dict[str, Any]
    async def start(self) -> Generator[Incomplete]:
        """Start Request.

        Initiates requests for the specified start URLs using Scrapy requests with additional
        meta information for playwright usage.
        """
