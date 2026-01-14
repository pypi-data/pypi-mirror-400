from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, trim_table_empty_cells as trim_table_empty_cells, validate_file_extension as validate_file_extension
from gllm_docproc.model.element import Element as Element, FOOTER as FOOTER, HEADER as HEADER, TABLE as TABLE, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.model.element_metadata import DOCX as DOCX, ElementMetadata as ElementMetadata
from typing import Any

class PythonDOCXLoader(BaseLoader):
    """A class for loading and processing DOCX document using PythonDOCXLoader.

    This class defines the structure for loading and processing DOCX document to retrieve required values
    (Header, Body (Text and Table), Footer). It implements the 'load' method to handle DOCX loading
    from a given file path.

    PythonDOCXLoader is used to extract the Header, Body (Text and Table), Footer and metadata from the DOCX document.

    Methods:
        load(source, loaded_elements, **kwargs): Load a DOCX document.
    """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load and process a DOCX document specified by the file path and name (source).

        This method defines the process of loading a DOCX document using its file path.
        It uses PythonDOCX to extract element text (with text structure) and table from the DOCX document.

        Args:
            source (str): The path to the DOCX document file.
            loaded_elements (list[dict[str, Any]]): A list of dictionaries containing loaded content and metadata.
            **kwargs (Any): Additional keyword arguments for the loader.

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing loaded content and metadata.
        """
