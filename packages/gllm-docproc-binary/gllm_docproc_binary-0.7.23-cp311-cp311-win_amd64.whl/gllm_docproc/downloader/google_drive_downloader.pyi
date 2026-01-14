from _typeshed import Incomplete
from gllm_docproc.downloader import BaseDownloader as BaseDownloader
from typing import Any

class GoogleDriveDownloader(BaseDownloader):
    """A class for downloading files from Google Drive using BOSA connector for Google Drive integration."""
    bosa: Incomplete
    user: Incomplete
    google_drive: Incomplete
    logger: Incomplete
    def __init__(self, api_key: str, identifier: str, secret: str, api_base_url: str = 'https://api.bosa.id') -> None:
        '''Initialize the GoogleDriveDownloader.

        Args:
            api_key (str): The API key for the BOSA API.
            identifier (str): The identifier for the BOSA user.
            secret (str): The secret for the BOSA user.
            api_base_url (str, optional): The base URL for the BOSA API. Defaults to "https://api.bosa.id".
        '''
    def download(self, source: str, output: str, **kwargs: Any) -> list[str]:
        """Download a file from Google Drive to the output directory.

        Args:
            source (str): The Google Drive file ID or URL.
            output (str): The output directory where the downloaded file will be saved.
            **kwargs (Any): Additional keyword arguments.

        Kwargs:
            export_format (str, optional): The export format for the file.

        Returns:
            list[str]: A list containing the path(s) to the successfully downloaded file(s).

        Raises:
            ValueError: If file ID cannot be extracted or no files are returned from Google Drive.
        """
