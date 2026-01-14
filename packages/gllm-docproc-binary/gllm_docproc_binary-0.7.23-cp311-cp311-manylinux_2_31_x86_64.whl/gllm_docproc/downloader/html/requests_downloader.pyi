from _typeshed import Incomplete
from gllm_docproc.downloader import BaseDownloader as BaseDownloader
from gllm_docproc.downloader.html.utils import generate_filename_from_url as generate_filename_from_url
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, HTML as HTML
from gllm_docproc.utils.file_utils import save_to_json as save_to_json
from typing import Any

class RequestsDownloader(BaseDownloader):
    """A class for downloading HTML content from web pages and returning JSON format.

    This class downloads HTML content from a given URL and returns it in a specific
    dictionary format containing ElementMetadata and the decoded HTML content.
    """
    max_retries: Incomplete
    timeout: Incomplete
    proxies: Incomplete
    session: Incomplete
    logger: Incomplete
    def __init__(self, max_retries: int = 3, timeout: float | None = None, proxies: dict[str, str] | None = None) -> None:
        '''Initialize the RequestsDownloader.

        Args:
            max_retries (int, optional): The maximum number of retries for failed downloads. Defaults to 3.
            timeout (float | None, optional): The timeout for the download request in seconds. Defaults to None.
            proxies (dict[str, str] | None, optional): Dictionary of proxy servers to use. Defaults to None.
                Example: {"http": "http://proxy.example.com:8080", "https": "https://proxy.example.com:8080"}
        '''
    def download(self, source: str, output: str, **kwargs: Any) -> list[str]:
        """Download HTML content from the source URL and save as JSON file.

        Args:
            source (str): The URL to download HTML content from.
            output (str): The output directory where the downloaded JSON file will be saved.
            **kwargs (Any): Additional keyword arguments.

        kwargs:
            timeout (float | None, optional): Override the timeout for this specific request.
            max_retries (int, optional): Override the max_retries for this specific request.
            proxies (dict[str, str] | None, optional): Override the proxies for this specific request.

        Returns:
            list[str]: A list containing the file path of the saved JSON file.

        Raises:
            requests.RequestException: If the download fails after all retries.
        """
