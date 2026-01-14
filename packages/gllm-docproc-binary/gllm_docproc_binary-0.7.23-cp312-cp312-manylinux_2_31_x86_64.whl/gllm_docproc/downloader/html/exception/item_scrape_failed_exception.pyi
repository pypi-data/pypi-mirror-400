from _typeshed import Incomplete

class ItemScrapeFailedException(Exception):
    """Exception raised when an item fails to be scraped.

    Attributes:
        message (str): Optional. The error message indicating the reason for the item scrape failure.
    """
    message: Incomplete
    def __init__(self, message: str = 'Item failed to be scraped.') -> None:
        '''Initialize the ItemScrapeFailedException.

        Args:
            message (str): Optional. The error message indicating the reason for the item scrape failure.
                Defaults to "Item failed to be scraped."
        '''
