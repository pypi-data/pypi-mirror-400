from gllm_docproc.loader.html.exception import HtmlLoadException as HtmlLoadException
from gllm_docproc.model.element import Element as Element
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, HTML as HTML
from gllm_docproc.utils.html_constants import HTMLTags as HTMLTags, MetaDataKeys as MetaDataKeys
from scrapy.http import HtmlResponse
from typing import Any

def is_html_content(content: str) -> bool:
    '''Check if the provided content appears to be HTML.

    This function performs a case-insensitive check to determine if the content contains HTML tags,
    specifically by searching for the opening and closing HTML tags ("<html" and "</html>").

    Args:
        content (str): The content to check.

    Returns:
        bool: True if the content is identified as HTML; False otherwise.
    '''
def extract_html_head(response: HtmlResponse, element_metadata: dict[str, Any] | None) -> ElementMetadata:
    """Extracts metadata from an HTML response.

    Args:
        response (HtmlResponse): The HTML response.
        element_metadata (dict[str, Any] | None): The element metadata.

    Returns:
        ElementMetadata: A class containing element metadata.

    Raises:
        HtmlLoadException: If an error occurs during the extraction process.
    """
def extract_html_title_tag(metadata: ElementMetadata) -> list[Element]:
    """Gets the title element as a Element.

    Args:
        metadata (ElementMetadata): A class containing element metadata.

    Returns:
        List[Element]: List containing a single Element instance representing the title element.
    """
def resolve_relative_url(url: str, base_url: str) -> str:
    '''Resolve a relative URL against a base URL.

    This function handles various relative URL patterns:
    1. Relative paths: "image.png", "folder/image.png"
    2. Parent directory: "../image.png"
    3. Absolute paths: "/image.png"
    4. Already absolute URLs are returned as-is

    Args:
        url (str): The URL to resolve (may be relative or absolute).
        base_url (str): The base URL to resolve against (can be a full path like
            "http://example.com/articles/news/news_id").

    Returns:
        str: The resolved absolute URL, or the original url if it\'s already absolute
            or base_url is invalid.
    '''
