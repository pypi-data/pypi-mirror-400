from _typeshed import Incomplete
from gllm_docproc.downloader.html.exception import ZyteApiKeyNotProvidedException as ZyteApiKeyNotProvidedException
from gllm_docproc.downloader.html.scraper.scraper.spiders import ScrapeSpider as ScrapeSpider, ZyteScrapeSpider as ZyteScrapeSpider
from scrapy import Spider as Spider
from typing import Any

class WebScraperExecutor:
    '''A utility class for initiating and running web scraping processes using Scrapy spiders.

    This class supports multiple spider types such as PlaywrightScrapeSpider, ZyteScrapeSpider, CrawlBaseSpider,
    and CrawlSitemapSpider. It utilizes multiprocessing to run the scraping process concurrently.

    Methods:
        __init__: Initializes the WebScraperExecutor instance.
        get_html_strings: Initiates the Scrapy spider and starts the scraping process using multiprocessing.
        get_spider_class: Gets the appropriate Scrapy spider class based on the provided spider type.
        _crawler_results: Appends the provided item to the list of items.
        _create_crawl_process: Creates and runs a Scrapy crawl process for a specific spider.
        _is_connected_to_internet: Checks if the system is connected to the internet.

    Raises:
        ZyteApiKeyNotProvidedException: If the spider is "zyte" but the Zyte API key is not provided.
    '''
    results: Incomplete
    items: dict[str, bytes | Exception]
    kwargs: Incomplete
    spider: Incomplete
    def __init__(self, urls: list[str] | str, **kwargs: Any) -> None:
        """Initializes the WebScraperExecutor instance.

        Args:
            urls (List[str] | str): The URLs to be scraped.
            **kwargs (Dict[str, Any]): Additional keyword arguments.
        """
    def get_url_content_pairs(self) -> list[tuple[str, bytes | Exception]]:
        '''Initiates the Scrapy spider and starts the scraping process using multiprocessing.

        Returns:
            List: A list of scraped url and html content.

        Raises:
            ZyteApiKeyNotProvidedException: If the spider is "zyte" but the Zyte API key is not provided.
        '''
