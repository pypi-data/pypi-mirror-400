def is_valid_url(url: str) -> bool:
    """Checks if the provided URL is valid.

    Args:
        url (str): The URL to be validated.

    Returns:
        bool: True if the URL is valid; False otherwise.
    """
def clean_url(url: str) -> str:
    '''Return a deterministic filename stem by sanitizing only disallowed characters.

    Only these characters are replaced with underscores: < > : " / \\ | ? *

    Example:
        https://www.bca.co.id/promo-bca -> https_www.bca.co.id_promo-bca

    Args:
        url (str): The URL to clean.

    Returns:
        str: A sanitized filename stem with only the listed characters replaced.
    '''
def generate_filename_from_url(url: str, max_filename_len: int = 128) -> str:
    """Generate a sanitized, unique, and length-safe filename stem from a URL.

    The returned value is a filename stem (no extension). It is composed of a sanitized
    version of the URL plus a uniqueness suffix consisting of a short random token.
    The function also trims the base so that the final filename stem will not exceed
    the specified maximum length.

    Args:
        url (str): The URL to derive the filename from.
        max_filename_len (int, optional): Maximum total filename length for the stem.
            Defaults to 128.

    Returns:
        str: A safe filename stem (no extension) that is unique and within length constraints.
    """
