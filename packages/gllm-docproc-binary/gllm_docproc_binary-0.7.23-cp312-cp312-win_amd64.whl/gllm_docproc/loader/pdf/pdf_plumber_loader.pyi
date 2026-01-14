from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, trim_table_empty_cells as trim_table_empty_cells, validate_file_extension as validate_file_extension
from gllm_docproc.loader.pdf.pdf_loader_utils import bbox_to_coordinates as bbox_to_coordinates, merge_loaded_elements_by_coordinates as merge_loaded_elements_by_coordinates
from gllm_docproc.model.element import Element as Element, TABLE as TABLE
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, PDF as PDF
from typing import Any

class PDFPlumberLoader(BaseLoader):
    """A class for loading and processing PDF document using PDFPlumberLoader.

    This class defines the structure for loading and processing PDF document to retrieve required values
    (table and metadata). It implements the 'load' method to handle PDF loading from a given file path.

    PDFPlumberLoader is used to extract the TABLE and metadata from the PDF document.

    Methods:
        load(source, loaded_elements, **kwargs): Load a PDF document.
    """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load and process PDF document specified by the file path and name (source).

        This method defines the process of loading and extracting table information from
        PDF document using PDF Plumber library using its file path and name.

        Args:
            source (str): The path to the PDF document file.
            loaded_elements (list[dict[str, Any]]): A list of dictionaries containing loaded content and metadata.
            **kwargs (Any): Additional keyword arguments for the loader.

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing loaded content and metadata.
        """
