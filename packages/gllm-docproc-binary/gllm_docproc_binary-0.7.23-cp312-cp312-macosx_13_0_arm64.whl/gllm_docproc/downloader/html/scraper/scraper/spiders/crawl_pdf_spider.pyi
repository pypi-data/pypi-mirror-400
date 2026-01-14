from .crawl_spider import CrawlBaseSpider as CrawlBaseSpider
from _typeshed import Incomplete
from collections.abc import Generator
from gllm_docproc.downloader.html.utils import clean_url as clean_url
from scrapy.http import Request, Response

class CrawlPDFSpider(CrawlBaseSpider):
    """Scrapy CrawlSpider to crawl websites and save responses as PDFs using Playwright.

    Attributes:
        name (str): The name of the spider - 'crawl_pdf_spider'.
        allowed_domains (list): The allowed domains for spider to crawl.
        start_urls (list): The starting URLs for the spider to initiate crawling.
        custom_settings (dict): Custom settings for the spider, including item pipelines configuration.
        rules (tuple): The rules to be followed during the crawling process.
    """
    name: str
    def add_playwright(self, request: Request, _: Response):
        """Adds playwright meta information to the request."""
    async def start(self) -> Generator[Incomplete]:
        """Start Request.

        Initiates requests for the specified start URLs using Scrapy requests with additional
        meta information for playwright usage.
        """
    async def parse_web(self, response: Response):
        """Parses the response obtained from the website, distinguishing between HTML content and other file types."""
