from abc import ABC, abstractmethod
from typing import Any

class BaseDownloader(ABC):
    """Base class for document downloader."""
    @abstractmethod
    def download(self, source: str, output: str, **kwargs: Any) -> list[str] | None:
        """Download source to the output directory.

        Args:
            source (str): The source to be downloaded.
            output (str): The output directory where the downloaded source will be saved.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            list[str] | None: A list of file paths of successfully downloaded files.
                If no files are downloaded, an empty list should be returned.
                Returning None is only for backward compatibility and should be avoided in new implementations.
        """
