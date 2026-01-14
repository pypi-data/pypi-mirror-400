from _typeshed import Incomplete
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, validate_file_extension as validate_file_extension
from gllm_docproc.loader.pdf.pymupdf_utils import bbox_to_coordinates as bbox_to_coordinates, convert_page_to_image_base64 as convert_page_to_image_base64, create_page_element as create_page_element, extract_image_element as extract_image_element, find_related_link as find_related_link
from gllm_docproc.model.element import Element as Element, IMAGE as IMAGE, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, PDF as PDF
from typing import Any

class PyMuPDFLoader(BaseLoader):
    """A class for loading and processing PDF document using PyMuPDF.

    This class defines the structure for loading and processing PDF document to retrieve required values
    (text and image in base64 format). It implements the 'load' method to handle PDF loading from a given file path.

    PyMuPDFLoader is used to extract the TEXT and IMAGE in base64 format from the PDF document.
    Text loader have to be the first loader in the pipeline. This prioritization is because subsequent
    loaders like the Table Loader may contain overlapping information with the Text Loader.
    Therefore, these subsequent loaders rely on the output from the Text Loader. They merge the
    loaded elements and filter out any duplicates by using the information provided by the Text Loader.

    Methods:
        load(source, loaded_elements, **kwargs): Load a PDF document.
    """
    fallback_to_image: Incomplete
    page_dpi: Incomplete
    def __init__(self, fallback_to_image: bool = True, page_dpi: int = 150) -> None:
        """Initialize the PyMuPDF Loader.

        Args:
            fallback_to_image (bool, optional): A boolean to determine if the loader should fall back to
                rendering the entire page as a base64-encoded image when no text or embedded images are found.
                Defaults to True.
            page_dpi (int, optional): The DPI of the page image. Defaults to 150.
        """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load and process a PDF document specified by the file path and name (source).

        This method defines the process of loading a PDF document using its file path.
        It uses PyMuPDF to extract element text and element image from the PDF document.

        Args:
            source (str): The path to the PDF document file.
            loaded_elements (list[dict[str, Any]]): A list of dictionaries containing loaded content and metadata.
            **kwargs (Any): Additional keyword arguments for the loader.

        Kwargs:
            original_source (str, optional): The original source of the document.
            hyperlink_as_markdown (bool, optional): A boolean to determine if the hyperlink should be in
                markdown format. Defaults to True.
            sort_elements (Callable, optional): A callable function to sort the elements in every page.
                Defaults to None. Means no sorting will be done.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing loaded content and metadata.
        """
