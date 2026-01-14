from _typeshed import Incomplete
from pydantic import BaseModel
from types import TracebackType
from typing import BinaryIO

class ValidatorInput(BaseModel):
    """File object used for validation.

    Attributes:
        name (str): File name (basename).
        extension (str): File extension without leading dot, lowercased (e.g., 'pdf').
        size (int): File size in bytes.
        file (BinaryIO): Open binary file handle for content-based validations.
        content_type (str | None): Optional content type (MIME), if known.
    """
    model_config: Incomplete
    name: str
    extension: str
    size: int
    file: BinaryIO
    content_type: str | None
    @classmethod
    def from_path(cls, path: str) -> ValidatorInput:
        """Create a ValidatorInput from a local path (opens in rb mode).

        Args:
            path (str): The file path to create ValidatorInput from.

        Returns:
            ValidatorInput: A ValidatorInput instance.
        """
    def close(self) -> None:
        """Close the underlying file handle if owned by this object.

        This method is idempotent and will not raise an error if the file is already closed.
        """
    def __enter__(self) -> ValidatorInput:
        """Enter the runtime context related to this object.

        Returns:
            ValidatorInput: The ValidatorInput instance itself.
        """
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        """Exit the runtime context and close the file handle if owned.

        Args:
            exc_type (type[BaseException] | None): The exception type, if any.
            exc_val (BaseException | None): The exception value, if any.
            exc_tb (TracebackType | None): The traceback, if any.
        """
