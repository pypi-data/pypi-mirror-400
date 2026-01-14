from .crawl_sitemap_spider import CrawlSitemapSpider as CrawlSitemapSpider
from scrapy.crawler import Crawler
from typing import Any

class CrawlSitemapLinkSpider(CrawlSitemapSpider):
    """A Scrapy spider designed to scrape links from the sitemaps.

    This spider uses the CrawlSitemapSpider base class to follow the sitemap links provided in the
    robots.txt file of the website. It parses each page and extracts the URLs of the pages. If

    Attributes:
        name (str): The name of the spider - 'crawl_sitemap_link_spider'.
        custom_settings (dict): Custom settings for the spider, including the log level and log file.
    """
    name: str
    custom_settings: dict[str, Any]
    @classmethod
    def from_crawler(cls, crawler: Crawler, *args: Any, **kwargs: Any):
        """Creates a new instance of the spider.

        Args:
            crawler (scrapy.crawler.Crawler): The Scrapy crawler object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            CrawlSitemapLinkSpider: A new instance of the spider.
        """
