from _typeshed import Incomplete

class HtmlLoadException(Exception):
    """Custom exception for handling HtmlLoadException errors."""
    message: Incomplete
    def __init__(self, message: str) -> None:
        """Initialize the HtmlLoadException."""
