from abc import ABC, abstractmethod
from typing import Any

class BaseDataGenerator(ABC):
    """Base class for data generator."""
    @abstractmethod
    def generate(self, elements: Any, **kwargs: Any) -> Any:
        """Generates data for a list of chunks.

        Args:
            elements (Any): The elements to be used for generating data / metadata. ideally formatted as List[Dict].
            **kwargs (Any): Additional keyword arguments for customization.

        Returns:
            Any: The generated data, ideally formatted as List[Dict]. Each dictionary within
                the list are recommended to follows the structure of model 'Element',
                to ensure consistency and ease of use across Document Processing Orchestrator.
        """
