from _typeshed import Incomplete
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, validate_file_extension as validate_file_extension
from gllm_docproc.loader.pdf.azure_ai_document_intelligence_raw_loader import AzureAIDocumentIntelligenceRawLoader as AzureAIDocumentIntelligenceRawLoader
from gllm_docproc.loader.pdf.pdf_loader_utils import merge_loaded_elements_by_coordinates as merge_loaded_elements_by_coordinates
from gllm_docproc.model.element import Element as Element, TABLE as TABLE, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, IMAGE as IMAGE, PDF as PDF
from gllm_docproc.model.media import Media as Media, MediaSourceType as MediaSourceType, MediaType as MediaType
from typing import Any

class AzureAIDocumentIntelligenceLoader(BaseLoader):
    """Azure AI Document Intelligence Loader class.

    This class provides a loader for extracting text, tables, and images from PDF files
    using the Azure AI Document Intelligence API. It implements the 'load' method to handle document
    loading from a given source.

    Methods:
        load(source, loaded_elements, **kwargs): Load and process a document.
    """
    INCH_TO_POINT: int
    endpoint: Incomplete
    key: Incomplete
    logger: Incomplete
    def __init__(self, endpoint: str, key: str) -> None:
        """Initializes the Azure AI Document Intelligence Loader class.

        Args:
            endpoint (str): The endpoint for the Azure AI Document Intelligence API.
            key (str): The key for the Azure AI Document Intelligence API.
        """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load and process a document using the Azure AI Document Intelligence API.

        Args:
            source (str): The source of the document to be processed.
            loaded_elements (list[dict[str, Any]], optional): A list of dictionaries containing loaded content and
                metadata. Defaults to None.
            **kwargs (Any): Additional keyword arguments for the loader.

        Kwargs:
            raw_output (dict[str, Any], optional): The raw output from the Azure AI Document Intelligence Raw Loader.
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing loaded content and metadata.
        """
