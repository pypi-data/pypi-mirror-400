from _typeshed import Incomplete
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import validate_file_extension as validate_file_extension
from typing import Any

class GLAIRVisionOCRLoader(BaseLoader):
    """GLAIR Vision OCR Loader class.

    This class provides a loader for extracting text and table from PDF file using the GLAIR Vision OCR API.
    It implements the 'load' method to handle document loading from a given source.

    Methods:
        load(source, loaded_elements, **kwargs): Load and process a document.
    """
    username: Incomplete
    password: Incomplete
    api_key: Incomplete
    def __init__(self, username: str, password: str, api_key: str) -> None:
        """Initializes the GLAIRVisionOCRLoader class.

        Args:
            username (str): The username for the GLAIR Vision OCR API.
            password (str): The password for the GLAIR Vision OCR API.
            api_key (str): The API key for the GLAIR Vision OCR API.
        """
    def load(self, source: str, loaded_elements: Any = None, **kwargs: Any) -> dict[str, Any]:
        """Load and process a document using the GLAIR Vision OCR API.

        This method loads a PDF document from a given source and extracts text and table using the GLAIR Vision OCR API.

        Args:
            source (str): The source of the document to be processed.
            loaded_elements (Any): The loaded elements from previous loaders.
            **kwargs (Any): Additional keyword arguments for customization.

        Returns:
            dict: The OCR response from the GLAIR Vision OCR API.
        """
