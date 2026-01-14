from abc import ABC, abstractmethod
from typing import Any

class BaseParser(ABC):
    """Base class for document parser.

    This class serves as the base for document parser, which will define the structure for every
    content of document.

    Methods:
        parse(loaded_elements, **kwargs): Abstract method to parse a document.
    """
    @abstractmethod
    def parse(self, loaded_elements: Any, **kwargs: Any) -> Any:
        """Parse loaded elements to get element structure.

        This method is abstract and must be implemented in subclasses.
        It defines the process of parsing a document using loaded elements.

        Args:
            loaded_elements (Any): The loaded elements from loader. ideally formatted as List[Dict].
            **kwargs (Any): Additional keyword arguments for customization.

        Returns:
            Any: The parsed document, ideally formatted as List[Dict]. Each dictionary within
                the list are recommended to follows the structure of model 'Element',
                to ensure consistency and ease of use across Document Processing Orchestrator.
        """
