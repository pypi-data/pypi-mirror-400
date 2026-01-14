from gllm_docproc.loader.html.utils.flat_table_utils import FlatTableUtils as FlatTableUtils
from gllm_docproc.loader.html.utils.html_utils import resolve_relative_url as resolve_relative_url
from gllm_docproc.model.element import Element as Element
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata
from gllm_docproc.utils.html_constants import ContentDataKeys as ContentDataKeys, HTMLTags as HTMLTags, ItemDataKeys as ItemDataKeys
from parsel import Selector, SelectorList

def merge_html_elements(content_selector: Selector | SelectorList[Selector], contents: list[Element], html_head: ElementMetadata) -> list[Element]:
    """For non-base element, add metadata and merge children into one with parent element.

    1. Add its HTML tag into its metadata
    2. For some HTML tags, combine its children into a single element into the parent, for example:
        1. Combine <ul> / <ol> children into a single element
        2. Combine <a> children to become [text](https://link.com)

    Args:
        content_selector(Selector | SelectorList[Selector]): The content selector representing the HTML element.
        contents (list[Element]): list of Element instances representing the contents of the HTML element.
        html_head (ElementMetadata): The metadata extracted from the HTML head.

    Returns:
        list[Element]: list of Element instances after handling the contents based on the parent tag.
    """
