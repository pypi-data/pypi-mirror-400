from _typeshed import Incomplete
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import validate_file_extension as validate_file_extension
from typing import Any

class AzureAIDocumentIntelligenceRawLoader(BaseLoader):
    """Azure AI Document Intelligence Raw Loader class.

    This class provides a loader for extracting text, tables, and images from PDF files
    using the Azure AI Document Intelligence API. It implements the 'load' method to handle document
    loading from a given source.

    Methods:
        load(source, loaded_elements, **kwargs): Load and process a document.
    """
    endpoint: Incomplete
    key: Incomplete
    def __init__(self, endpoint: str, key: str) -> None:
        """Initializes the AzureAILoader class.

        Args:
            endpoint (str): The endpoint for the Azure AI Document Intelligence API.
            key (str): The key for the Azure AI Document Intelligence API.
        """
    def load(self, source: str, loaded_elements: Any = None, **kwargs: Any) -> dict[str, Any]:
        '''Load and process a document using the Azure AI Document Intelligence API.

        This method sends a request to the Azure AI Document Intelligence API to extract information
        from a PDF file. It returns the extracted information in a dictionary format, without any
        additional processing.

        Kwargs:
            model_id (str, optional): The model used for document analysis. Azure AI Document Intelligence API
                provides several prebuilt models for document analysis, check for available models at:
                https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept-model-overview?
                view=doc-intel-4.0.0#model-analysis-features
                Defaults to "prebuilt-layout".
            features (list[str], optional): The add-on capabilities. Document Intelligence supports more sophisticated
                analysis capabilities. These optional features can be enabled and disabled depending on the scenario
                of the document extraction. Check for available add on capabilities at:
                https://learn.microsoft.com/en-us/python/api/overview/azure/ai-documentintelligence-readme?
                view=azure-python-preview#add-on-capabilities
                Defaults to an empty list.

        Args:
            source (str): The source of the document to be processed.
            loaded_elements (Any): A list of loaded elements to be processed.
            **kwargs (Any): Additional keyword arguments.
        '''
