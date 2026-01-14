from _typeshed import Incomplete

class UnsupportedFileExtensionError(Exception):
    """An exception for unsupported file extension."""
    message: Incomplete
    def __init__(self, ext: str, loader_name: str) -> None:
        """Initialize the exception."""
