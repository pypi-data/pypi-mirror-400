from _typeshed import Incomplete

class ZyteApiKeyNotProvidedException(Exception):
    """Custom exception raised when the Zyte API key is not provided.

    Attributes:
        message (str): Optional. The error message associated with the exception.
    """
    message: Incomplete
    def __init__(self, message: str = 'Zyte API Key not provided.') -> None:
        '''Initialize the ZyteApiKeyNotProvidedException.

        Args:
            message (str, optional): The error message associated with the exception.                 Defaults to "Zyte API Key not provided."
        '''
