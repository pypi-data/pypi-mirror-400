from _typeshed import Incomplete
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, trim_table_empty_cells as trim_table_empty_cells, validate_file_extension as validate_file_extension
from gllm_docproc.model.element import Element as Element, FOOTER as FOOTER, HEADER as HEADER, IMAGE as IMAGE, TABLE as TABLE, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.model.element_metadata import DOCX as DOCX, ElementMetadata as ElementMetadata
from gllm_docproc.model.media import Media as Media, MediaSourceType as MediaSourceType, MediaType as MediaType
from typing import Any

class DOCX2PythonLoader(BaseLoader):
    """A class for loading and processing DOCX document using docx2python library.

    This class defines the structure for loading and processing DOCX document to retrieve required values
    (text, table, image, header, footer footnote, endnote). It implements the 'load' method to handle DOCX loading
    from a given file path.

    DOCX2PythonLoader is used to extract the text, table, image, header, footer, footnote, endnote
    from the DOCX document.

    Methods:
        load(source, loaded_elements, **kwargs): Load a DOCX document.
    """
    duplicate_merged_cells: Incomplete
    def __init__(self, duplicate_merged_cells: bool = True) -> None:
        """Initialize the DOCX2PythonLoader.

        Args:
            duplicate_merged_cells (bool): A boolean value indicating whether to duplicate merged cells.
        """
    def load(self, source: str, loaded_elements: list[dict[str, str]] | None = None, **kwargs: Any) -> list[dict[str, str]]:
        """Load and process a DOCX document specified by the file path and name (source).

        This method defines the process of loading a DOCX document using its file path.
        It extracts the text, table, image, header, footer, footnote, endnote from the DOCX document.

        Args:
            source (str): The file path of the DOCX document.
            loaded_elements (list[dict[str, str]] | None): A list of loaded elements containing text content
                and metadata.
            **kwargs (Any): Additional keyword arguments for loading the DOCX document.

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing loaded content and metadata.
        """
