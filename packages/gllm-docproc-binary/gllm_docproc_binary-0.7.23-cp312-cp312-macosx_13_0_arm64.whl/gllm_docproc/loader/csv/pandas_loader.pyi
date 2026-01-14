from _typeshed import Incomplete
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, validate_file_extension as validate_file_extension
from gllm_docproc.model.element import Element as Element, TABLE as TABLE
from gllm_docproc.model.element_metadata import CSV as CSV, ElementMetadata as ElementMetadata
from typing import Any

CSV_VARIANTS: Incomplete

class PandasLoader(BaseLoader):
    """A class used to load and process delimited text files using the pandas library.

    This class inherits from the BaseLoader class and overrides its methods to provide
    functionality for loading delimited text files with different separators:
    - CSV (Comma-Separated Values): Uses commas (,) as separators between values
    - TSV (Tab-Separated Values): Uses tabs (\\t) as separators between values
    - PSV (Pipe-Separated Values): Uses pipe characters (|) as separators between values
    - SSV (Space-Separated Values): Uses spaces as separators between values

    It provides methods to extract tables from the document and convert them into elements.

    Methods:
        load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any)
            -> list[dict[str, Any]]: Load a delimited text file.
    """
    logger: Incomplete
    def __init__(self) -> None:
        """Initialize the PandasLoader class."""
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load a delimited text file.

        This method loads a delimited text file (CSV, TSV, PSV, SSV) and extracts the table elements.
        The method takes the source file path as input and returns a list of Element objects
        representing the tables in the document.

        Args:
            source (str): The path to the delimited text file to load.
            loaded_elements (list[dict[str, Any]]): The loaded elements from previous loaders.
            **kwargs (Any): Additional keyword arguments to pass to the loader.

        Kwargs:
            original_source (str, optional): The original source of the document.
            sep (str, optional): Delimiter to use. If not provided, will be auto-detected.
            encoding (str, optional): Encoding to use. Defaults to 'utf-8'.
            header (int | None, optional): Row number (0-based index) to use as column names.
                If None, no header row is assumed and numeric column names are generated.

        Returns:
            list[dict[str, Any]]: The loaded elements from the delimited text file.

        Raises:
            UnsupportedFileExtensionError: If the file extension is not supported.
        """
