from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, trim_table_empty_cells as trim_table_empty_cells, validate_file_extension as validate_file_extension
from gllm_docproc.loader.pdf.pdf_loader_utils import merge_loaded_elements_by_coordinates as merge_loaded_elements_by_coordinates
from gllm_docproc.model.element import Element as Element, TABLE as TABLE
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, PDF as PDF
from typing import Any

class TabulaLoader(BaseLoader):
    """A class for loading PDF and extracting Table from PDF using Tabula.

    This class defines the structure for loading PDF and extracting Table from PDF using Tabula.
    It implements the 'load' method to handle the loading and extraction process.

    TabulaLoader is used to extract the TABLE and metadata from the PDF document.

    Methods:
        load(source, loaded_elements, **kwargs): Load the PDF file and extract Table from PDF using Tabula.
    """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load the PDF file and extract Table from PDF using Tabula.

        Args:
            source (str): The file path of the PDF document.
            loaded_elements (list[dict[str, Any]]): A list of loaded elements from the PDF document.
            **kwargs (Any): Additional keyword arguments.

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing loaded content and metadata.
        """
