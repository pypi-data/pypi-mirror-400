from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, validate_file_extension as validate_file_extension
from gllm_docproc.model.element import Element as Element, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, PDF as PDF
from typing import Any

class PDFMinerLoader(BaseLoader):
    """A class for loading and processing PDF document using PDFMiner.

    This class defines the structure for loading and processing PDF document to retrieve required values
    (text and metadata). It implements the 'load' method to handle PDF loading from a given file path.

    PDFMinerLoader is used to extract the TEXT and metadata from the PDF document.
    Text loader have to be the first loader in the pipeline. This prioritization is because subsequent
    loaders like the Table Loader may contain overlapping information with the Text Loader.
    Therefore, these subsequent loaders rely on the output from the Text Loader. They merge the
    loaded elements and filter out any duplicates by using the information provided by the Text Loader.

    Methods:
        load(source, loaded_elements, **kwargs): Load a PDF document.
    """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load and process a PDF document specified by the file path and name (source).

        This method defines the process of loading a PDF document using its file path.
        It uses PDFMiner to extract element text and element metadata from the PDF document.

        Args:
            source (str): The path to the PDF document file.
            loaded_elements (list[dict[str, Any]]): A list of dictionaries containing loaded content and metadata.
            **kwargs (Any): Additional keyword arguments for the loader.

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing loaded content and metadata.
        """
