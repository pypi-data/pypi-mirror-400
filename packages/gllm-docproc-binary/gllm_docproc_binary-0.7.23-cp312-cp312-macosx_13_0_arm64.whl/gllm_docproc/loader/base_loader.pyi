from abc import ABC, abstractmethod
from typing import Any

class BaseLoader(ABC):
    """An abstract base class for document loaders.

    This class defines the structure for loading and processing documents to retrieve
    required values. Subclasses are expected to implement the 'load' method
    to handle document loading from a given source.

    Methods:
        load(source, loaded_elements, **kwargs): Abstract method to load a document.
    """
    @abstractmethod
    def load(self, source: str, loaded_elements: Any = None, **kwargs: Any) -> Any:
        """Load and process a document.

        This method is abstract and must be implemented in subclasses.
        It defines the process of loading a document using its source.

        Args:
            source (str): Might be file path, URL, the content itself.
            loaded_elements (Any): The loaded elements from previous loaders. ideally formatted as List[Dict].
            **kwargs (Any): Additional keyword arguments for customization.

        Returns:
            Any: The loaded document, ideally formatted as List[Dict]. Each dictionary within
                the list are recommended to follows the structure of model 'Element',
                to ensure consistency and ease of use across Document Processing Orchestrator.
        """
