from abc import ABC, abstractmethod
from typing import Any

class BaseRequestHandler(ABC):
    """Base class for request handler."""
    @abstractmethod
    def handle_request(self, **kwargs: Any) -> None:
        """Handles a request.

        Args:
            **kwargs (Any): Arbitrary keyword arguments.
                            The implementing class is responsible to define the arguments

        Returns:
            None
        """
