from _typeshed import Incomplete
from gllm_docproc.downloader import BaseDownloader as BaseDownloader
from typing import Any

UNKNOWN_EXTENSION: str
FALLBACK_EXTENSION: str
MIME_TYPE_TO_EXTENSION_MAP: Incomplete

class DirectFileURLDownloader(BaseDownloader):
    """A class for downloading files from a direct file URL to the defined output directory."""
    stream_buffer_size: Incomplete
    max_retries: Incomplete
    timeout: Incomplete
    session: Incomplete
    logger: Incomplete
    def __init__(self, stream_buffer_size: int = 65536, max_retries: int = 3, timeout: int | None = None) -> None:
        """Initialize the DirectFileURLDownloader.

        Args:
            stream_buffer_size (int, optional): The size of the buffer for streaming downloads in bytes.
                Defaults to 64KB (65536 bytes).
            max_retries (int, optional): The maximum number of retries for failed downloads. Defaults to 3.
            timeout (int | None, optional): The timeout for the download request in seconds. Defaults to None.
        """
    def download(self, source: str, output: str, **kwargs: Any) -> list[str]:
        """Download source to the output directory.

        Args:
            source (str): The source to be downloaded.
            output (str): The output directory where the downloaded source will be saved.
            **kwargs (Any): Additional keyword arguments.

        kwargs:
            ca_certs_path (str, optional): The path to the CA certificates file. Defaults to None.
            extension (str, optional): The extension of the file to be downloaded. If not provided,
                the extension will be detected from the response headers or content mime type.

        Returns:
            list[str]: A list of file paths of successfully downloaded files.
        """
