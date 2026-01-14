from abc import ABC, abstractmethod
from typing import Any

class BaseDPORouter(ABC):
    """Base class for routing in document processing."""
    @abstractmethod
    def route(self, *args: Any, **kwargs: Any) -> Any:
        """Routes the input into different processing pipelines based on certain criteria.

        Args:
            *args (Any): Variable length argument list for routing parameters.
            **kwargs (Any): Arbitrary keyword arguments for additional routing configuration.

        Returns:
            Any: The result of the routing process.
        """
