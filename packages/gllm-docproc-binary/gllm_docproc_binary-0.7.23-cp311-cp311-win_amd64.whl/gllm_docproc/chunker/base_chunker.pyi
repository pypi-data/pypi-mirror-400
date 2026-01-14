from abc import ABC, abstractmethod
from typing import Any

class BaseChunker(ABC):
    """An abstract base class for chunker.

    This class segmenting or chunking elements based on contextual information.
    Subclasses are expected to implement the 'chunk' method to handle chunking elements.

    Methods:
        chunk(elements, **kwargs): Abstract method to chunk a document.
    """
    @abstractmethod
    def chunk(self, elements: Any, **kwargs: Any) -> Any:
        """Chunk a document.

        This method is abstract and must be implemented in subclasses.
        It defines the process of chunking information from elements.

        Args:
            elements (Any): The information to be chunked. ideally formatted as List[Dict].
            **kwargs (Any): Additional keyword arguments for customization.

        Returns:
            Any: The chunked information, ideally formatted as List[Dict]. Each dictionary within
                the list are recommended to follows the structure of model 'Element',
                to ensure consistency and ease of use across Document Processing Orchestrator.
        """
