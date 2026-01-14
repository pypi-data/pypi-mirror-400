from _typeshed import Incomplete
from gllm_docproc.loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, validate_file_extension as validate_file_extension
from gllm_docproc.loader.pdf.pymupdf_utils import convert_page_to_image_base64 as convert_page_to_image_base64, create_page_element as create_page_element
from gllm_docproc.model.element import Element as Element, PAGE as PAGE
from gllm_docproc.model.element_metadata import PDF as PDF
from typing import Any

class PDFPageLoader(BaseLoader):
    """PDF Page Loader class.

    This class defines the structure for loading PDF page level informations.
    It implements the 'load' method to load the PDF file from a given file path.

    Methods:
        load(source, loaded_elements, **kwargs): Load a PDF document.
    """
    dpi: Incomplete
    def __init__(self, dpi: int = 150) -> None:
        """Initialize the PDF Page Loader.

        Args:
            dpi (int, optional): Rendering resolution for each PDF page in Dots Per Inch (DPI).
                Higher values produce higher-quality images but increase memory usage.
                Defaults to 150.
        """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load and extract page level information from PDF document.

        Args:
            source (str): The file path to the PDF document.
            loaded_elements (list[dict[str, Any]] | None, optional): Previously loaded elements from the same source.
                If provided, new elements will be combined with existing ones. Defaults to None.
            **kwargs (Any): Additional keyword arguments for PDF processing configuration.

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing loaded content and metadata.
        """
