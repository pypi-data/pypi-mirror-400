from _typeshed import Incomplete
from gllm_docproc.loader.html.utils.html_utils import resolve_relative_url as resolve_relative_url
from gllm_docproc.loader.html.utils.removed_components import RemovedComponents as RemovedComponents
from gllm_docproc.loader.html.utils.string_utils import StringUtils as StringUtils
from gllm_docproc.model.element import Element as Element
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata
from gllm_docproc.model.media import Media as Media, MediaSourceType as MediaSourceType, MediaType as MediaType
from gllm_docproc.utils.html_constants import ContentDataKeys as ContentDataKeys, HTMLTags as HTMLTags
from parsel import Selector, SelectorList
from typing import Callable

def setup_mingw_path_for_cairosvg() -> None:
    """On Windows, add mingw bin to PATH so CairoSVG can find required DLLs.

    CairoSVG relies on DLLs (e.g., for font rendering and image processing) that may not be available
    in the default PATH. Adding the mingw bin directory ensures these dependencies are found,
    preventing import or runtime errors.
    """

CAIROSVG_AVAILABLE: bool
logger: Incomplete

def is_base_element(content_selector: Selector | SelectorList[Selector] | None, removed_components: RemovedComponents) -> bool:
    """Check if the given content selector represents a base element.

    A base element is determined by the type of element in the HTML document.
    Supported base elements include:
    1. Unsupported result (if content_selector is None)
    2. String text
    3. Removed Components (by class or tag) defined in RemovedComponents
    4. <input>
    5. <svg> image
    6. <img>
    7. <audio>, <video> (if multiple sources are given, select only the first one)
    8. <iframe> (cannot get the content of the iframe)
    9. <embed> (cannot get the content of the embed)
    10. <br>

    Args:
        content_selector (Selector | SelectorList[Selector] | None): The selector representing the HTML content.
        removed_components (RemovedComponents): Components to be removed from processing.

    Returns:
        bool: True if the content_selector represents a base element; False otherwise.
    """
def handle_base_element(content_selector: Selector | SelectorList[Selector] | None, html_head: ElementMetadata, removed_components: RemovedComponents) -> list[Element]:
    """Handle the base HTML element and generate Element instances.

    Args:
        content_selector (Selector | SelectorList[Selector] | None): The selector representing the HTML content.
        html_head (ElementMetadata): The metadata extracted from the HTML head.
        removed_components (RemovedComponents): Components to be removed from processing.

    Returns:
        list[Element]: A list of Element instances generated from the HTML content.
    """
def get_handler(tag: str) -> Callable[[Selector | SelectorList[Selector], ElementMetadata], list[Element]] | None:
    """Get the handler function corresponding to the given HTML tag.

    Args:
        tag (str): The HTML tag for which the handler function is requested.

    Returns:
        Callable[[Selector | SelectorList[Selector], ElementMetadata], list[Element]] | None: The handler
        function corresponding to the given HTML tag.
    """
