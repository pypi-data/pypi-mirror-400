from _typeshed import Incomplete
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, trim_table_empty_cells as trim_table_empty_cells, validate_file_extension as validate_file_extension
from gllm_docproc.model.element import Element as Element, IMAGE as IMAGE, PARAGRAPH as PARAGRAPH, TABLE as TABLE, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, PPTX as PPTX
from gllm_docproc.model.media import Media as Media, MediaSourceType as MediaSourceType, MediaType as MediaType
from typing import Any

UNTITLED_CHART: str

class PythonPPTXLoader(BaseLoader):
    """A class for loading and processing PPTX documents using PythonPPTXLoader.

    This class defines the structure for loading and processing a PPTX
    document to retrieve the content from its slides.
    It implements the 'load' method to handle PPTX loading from a given file path.

    PythonPPTXLoader is used to extract individual slides and
    their contents (such as text, tables, and images) and metadata from the PPTX document.

    Methods:
        load(source, loaded_elements, **kwargs): Load a PPTX document.
    """
    include_hidden_slides: Incomplete
    logger: Incomplete
    def __init__(self, include_hidden_slides: bool = False) -> None:
        """Initialize loader with option to include hidden slides.

        Args:
            include_hidden_slides (bool, optional): Whether to include hidden slides during loading. Defaults to False.
        """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load and process a PPTX document specified by the file path and name (source).

        This method defines the process of loading a PPTX document using its file path.
        It is responsible for extracting content from each slide, such as text, tables, and images.

        Args:
            source (str): The path to the PPTX document file.
            loaded_elements (list[dict[str, Any]]): A list of dictionaries containing loaded content and metadata.
            **kwargs (Any): Additional keyword arguments for the loader.

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing loaded content and metadata.
        """
