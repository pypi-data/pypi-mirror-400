from _typeshed import Incomplete
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import validate_file_extension as validate_file_extension
from typing import Any

class AdobePDFExtractLoader(BaseLoader):
    """Adobe PDF Extract Loader class.

    This class provides a loader for extracting information from PDF files using Adobe PDF Extract.
    It implements the 'load' method to load PDF files and extract information.

    Methods:
        load(source, loaded_elements, **kwargs): Loads a PDF file and extracts information.
    """
    credentials: Incomplete
    def __init__(self, client_id: str, client_secret: str) -> None:
        """Initializes the Adobe PDF Extract Loader.

        Args:
            client_id (str): The client ID for the Adobe PDF Extract API.
            client_secret (str): The client secret for the Adobe PDF Extract
        """
    def load(self, source: str, loaded_elements: Any = None, **kwargs: Any) -> dict[str, Any]:
        """Loads a PDF file and extracts information using Adobe PDF Extract.

        This method loads a PDF file and extracts information from the file using Adobe PDF Extract.
        The extracted information is returned as a dictionary. The extracted information includes text,
        tables, and other elements from the PDF file.

        Args:
            source (str): The source PDF file to load and extract information from.
            loaded_elements (Any): A list of loaded elements to be processed.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            dict[str, Any]: The extracted information as a dictionary
        """
