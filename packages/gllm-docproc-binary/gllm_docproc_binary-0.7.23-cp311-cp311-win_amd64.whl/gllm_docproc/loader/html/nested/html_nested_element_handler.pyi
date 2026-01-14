from gllm_docproc.loader.html.nested.dictionary_utils import DictionaryUtils as DictionaryUtils
from gllm_docproc.utils.html_constants import ContentDataKeys as ContentDataKeys, HTMLTags as HTMLTags

def get_element(content_selector) -> dict:
    """Get the element information from the specified content selector.

    Args:
        content_selector: The content selector representing the HTML element.

    Returns:
        dict: A dictionary containing information about the HTML element.
              - tag: HTML tag name.
              - class: CSS class of the element (if available).
              Additional keys may be added based on the specific element handler
    """
def get_handler(tag: str):
    """Gets the handler for the specified HTML tag.

    Args:
        tag (str): The HTML tag to get the handler for.

    Returns:
        Callable: The handler function for the specified HTML tag.
    """
