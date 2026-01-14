from abc import ABC, abstractmethod
from typing import Any

class BaseResponseHandler(ABC):
    """Base class for document converter."""
    @abstractmethod
    def handle_success_response(self, **kwargs: Any) -> None:
        """Handles a success response (successfully indexed).

        Args:
            **kwargs (Any): Arbitrary keyword arguments.
                                       The implementing class is responsible to define the arguments

        Returns:
            None
        """
    @abstractmethod
    def handle_deleted_response(self, **kwargs: Any) -> None:
        """Handles a deleted response (successfully deleted).

        Args:
            **kwargs (Any): Arbitrary keyword arguments.
                                       The implementing class is responsible to define the arguments

        Returns:
            None
        """
    @abstractmethod
    def handle_failed_response(self, **kwargs: Any) -> None:
        """Handles a failed response (either failed to index or failed to delete).

        Args:
            **kwargs (Any): Arbitrary keyword arguments.
                                       The implementing class is responsible to define the arguments

        Returns:
            None
        """
