from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, validate_file_extension as validate_file_extension
from gllm_docproc.model.element import Element as Element, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, PDF as PDF
from typing import Any

class PDFMinerWordLoader(BaseLoader):
    """PDFMinerWordLoader is used to extract the TEXT from the PDF document.

    This class defines the structure for loading PDF documents using PDFMiner per word.
    It implements the 'load' method to extract PDF information from a given file path.

    PDFMinerWordLoader is used to extract the TEXT from the PDF document.

    Methods:
        load(source, loaded_elements, **kwargs): Load a PDF document.
    """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load a PDF document.

        This method loads a PDF document from a given file path.

        Args:
            source (str): The file path of the PDF document.
            loaded_elements (list[dict[str, Any]]): The loaded elements.
            **kwargs (Any): Additional keyword arguments.

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: The loaded elements.
        """
