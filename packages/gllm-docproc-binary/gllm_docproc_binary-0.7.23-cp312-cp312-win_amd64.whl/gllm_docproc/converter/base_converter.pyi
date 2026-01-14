from abc import ABC, abstractmethod

class BaseConverter(ABC):
    """Base class for document converter."""
    @abstractmethod
    def convert(self, path_input: str, path_output: str) -> None:
        """Converts a document.

        Args:
            path_input (str): The path of the document to be converted.
            path_output (str): The path of the converted document.

        Returns:
            None
        """
