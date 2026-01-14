import fitz
from gllm_docproc.loader.pdf.pdf_loader_utils import bbox_to_coordinates as bbox_to_coordinates
from gllm_docproc.model.element import Element as Element, IMAGE as IMAGE
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata
from gllm_docproc.model.media import Media as Media, MediaSourceType as MediaSourceType, MediaType as MediaType
from typing import Any

def fix_image_with_transform(image_bytes: bytes, transform: tuple) -> bytes:
    """Apply the PDF affine transform (a,b,c,d,e,f) to an image using only the image's pixel grid.

    Ignores page size and DPI. Picks an output pixel size that preserves detail by default.
    Optionally pass px_per_point to control output density yourself.

    Args:
        image_bytes: The image data as bytes.
        transform: The PDF affine transform tuple (a,b,c,d,e,f).

    Returns:
        PNG bytes of the transformed image.
    """
def extract_image_element(image_instance: dict[str, Any], page_idx: int, element_metadata: ElementMetadata, page_layout_width: int, page_layout_height: int) -> Element | None:
    """Extract value (image in base64 format and other metadata) from image element.

    This method defines the process of extracting Image value in base64 format from image element.

    Args:
        image_instance (dict): The image instance.
        page_idx (int): The number of the page index.
        element_metadata (ElementMetadata): The element metadata.
        page_layout_width (int): The width of the page layout.
        page_layout_height (int): The height of the page layout.

    Returns:
        Element | None: An Element object containing image in base64 format and metadata.
            None if the image is empty.
    """
def find_related_link(text_rect: list[float], links: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Find the related link for a text rectangle.

    This method finds the related link for a text rectangle. It will return the link if the text
    rectangle intersects with the link rectangle.

    Args:
        text_rect (list[float]): The text rectangle.
        links (list[dict[str, Any]]): A list of links.

    Returns:
        dict[str, Any] | None: The related link if the text rectangle intersects with the link rectangle
            or None if the text rectangle does not intersect with the link rectangle.
    """
def convert_page_to_image_base64(page: fitz.Page, dpi: int = 150) -> str:
    """Convert a PDF page to a base64 encoded PNG image.

    Args:
        page (fitz.Page): The PDF page to convert.
        dpi (int, optional): Rendering resolution for each PDF page in Dots Per Inch (DPI).
            Higher values produce higher-quality images but increase memory usage. Defaults to 150.

    Returns:
        str: Base64 encoded PNG image.
    """
def create_page_element(page_image_base64: str, page_number: int, page: fitz.Page, base_element_metadata: ElementMetadata, structure: str = ...) -> Element:
    """Create a page element with the specified structure.

    This function creates an Element representing a page with its image content.
    It can be used to create either IMAGE or PAGE structure elements.

    Args:
        page_image_base64 (str): The page image in base64 format.
        page_number (int): The page number.
        page (fitz.Page): The PDF page.
        base_element_metadata (ElementMetadata): The base element metadata.
        structure (str, optional): The element structure type. Defaults to IMAGE.

    Returns:
        Element: The page element with the specified structure.
    """
