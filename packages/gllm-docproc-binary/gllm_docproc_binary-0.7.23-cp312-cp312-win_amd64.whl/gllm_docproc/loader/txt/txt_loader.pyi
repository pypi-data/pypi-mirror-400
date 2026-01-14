from _typeshed import Incomplete
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata
from gllm_docproc.model.element import Element as Element, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.model.element_metadata import TXT as TXT
from typing import Any

class TXTLoader(BaseLoader):
    """A class for loading text files (.txt) into a list of elements.

    Methods:
        load: Load a text file into a list of elements.
        is_text_file: Check if a file is a text file.
    """
    DEFAULT_SUPPORTED_PREFIX_MIME_TYPES: Incomplete
    logger: Incomplete
    supported_prefix_mime_types: Incomplete
    def __init__(self, supported_prefix_mime_types: list[str] | None = None) -> None:
        """Initialize the TXTLoader class.

        Args:
            supported_prefix_mime_types (list[str] | None, optional): The list of supported prefix mime types.
        """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load a text file into a list of elements.

        This method loads a text file into a list of elements.
        It uses the `is_text_file` method to check if the file is a text file.
        If the file is not a text file, the method will raise a ValueError.

        Args:
            source (str): The path to the text file.
            loaded_elements (list[dict[str, Any]]): The list of elements that have already been loaded.
            **kwargs: Additional keyword arguments.

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: A list of elements.

        Raises:
            ValueError: If the file is not a text file.
        """
    def is_text_file(self, source: str) -> bool:
        """Check if a file is a text file.

        This method uses the `magic` library to check if a file is a text file.

        Args:
            source (str): The path to the file.

        Returns:
            bool: True if the file is a text file, False otherwise.
        """
