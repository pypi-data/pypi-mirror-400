from _typeshed import Incomplete
from scrapy.crawler import Crawler
from scrapy.http import Response
from scrapy.spiders import SitemapSpider
from typing import Any

class CrawlSitemapSpider(SitemapSpider):
    """A Scrapy spider designed to scrape content from the sitemaps.

    This spider uses the SitemapSpider base class to follow the sitemap links provided in the
    robots.txt file of the website. It parses each page and extracts the URLs of the pages. If
    an error occurs during parsing, it logs the error.

    Attributes:
        name (str): The name of the spider - 'crawl_sitemap_spider'.
        sitemap_urls (list): The URLs of the sitemaps to start crawling from.
        allowed_domains (list): The domains that this spider is allowed to crawl.
        custom_settings (dict): Custom settings for the spider, including the log level and log file.
    """
    name: str
    custom_settings: dict[str, Any]
    sitemap_urls: Incomplete
    allowed_domains: Incomplete
    callback: Incomplete
    removed_components: Incomplete
    is_follow_page: Incomplete
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the CrawlSitemapSpider instance.

        The method initializes the CrawlSitemapSpider instance and sets the sitemap_urls, allowed_domains,
        and sitemap_from_robots attributes based on the provided arguments.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
    def parse(self, response: Response):
        """Parse the response.

        This method parses the response obtained from the website, extracts the URLs of the pages,
        and follows the links to the next pages.

        This method attempts to yield a dictionary containing the URL of the response. If an error occurs,
        it yields the URL and an error message.
        It also extracts the URLs of the next pages from the response and follows them.

        Args:
            response (scrapy.http.Response): The response object to parse.
        """
    @classmethod
    def from_crawler(cls, crawler: Crawler, *args: Any, **kwargs: Any) -> CrawlSitemapSpider:
        """Creates a new CrawlSitemapSpider instance and sets the custom settings.

        Args:
            crawler (scrapy.crawler.Crawler): The crawler object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            CrawlSitemapSpider: The CrawlSitemapSpider instance.
        """
