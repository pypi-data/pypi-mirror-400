from abc import ABC, abstractmethod

class BaseHouseKeeping(ABC):
    """Base class for document converter."""
    @abstractmethod
    def housekeeping(self, folder_path: str) -> None:
        """Placeholder method for performing housekeeping tasks on a specified folder.

        Args:
            folder_path (str): The path to the folder to perform housekeeping on.

        Returns:
            None
        """
