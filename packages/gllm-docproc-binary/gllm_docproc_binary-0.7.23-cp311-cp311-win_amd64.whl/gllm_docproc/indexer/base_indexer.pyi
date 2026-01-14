from abc import ABC, abstractmethod
from typing import Any

class BaseIndexer(ABC):
    """Base class for document converter."""
    @abstractmethod
    def index(self, elements: Any, **kwargs: Any) -> Any:
        """Index data from a source file into Elasticsearch.

        Args:
            elements (Any): The information to be indexed. Ideally formatted as List[Dict] and
                each Dict following the structure of model 'Element'.
            **kwargs (Any): Additional keyword arguments for customization.

        Returns:
            Any: The response from the indexing process.
        """
    @abstractmethod
    def delete(self, **kwargs: Any) -> Any:
        """Delete document from a vector DB.

        The arguments are not defined yet, it depends on the implementation.
        Some vector database will require: db_url, index_name, document_id.

        Args:
            **kwargs (Any): Additional keyword arguments for customization.

        Returns:
            Any: The response from the deletion process.
        """
