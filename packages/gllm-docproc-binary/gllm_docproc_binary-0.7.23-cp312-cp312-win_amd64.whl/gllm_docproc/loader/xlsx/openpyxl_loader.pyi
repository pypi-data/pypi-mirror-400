from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, validate_file_extension as validate_file_extension
from gllm_docproc.model.element import Element as Element, TABLE as TABLE
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, XLSX as XLSX
from typing import Any

class OpenpyxlLoader(BaseLoader):
    """A class used to load and process XLSX documents using the openpyxl library.

    This class inherits from the BaseLoader class and overrides its methods to provide
    functionality for loading XLSX documents. It provides methods to extract tables from
    the document, determine whether a row is a header based on its style attributes, and
    split a table into headers and body based on the row styles and header threshold.

    Methods:
        load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any)
            -> list[dict[str, Any]]: Load a XLSX document.
    """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load a XLSX document.

        This method loads a XLSX document and extracts the table elements from each sheet.
        The method takes the source file path as input and returns a list of Element objects
        representing the tables in the document.

        Args:
            source (str): The path to the XLSX document to load.
            loaded_elements (list[dict[str, Any]]): The loaded elements from previous loaders.
            **kwargs (Any): Additional keyword arguments to pass to the loader.

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: The loaded elements from the XLSX document.
        """
