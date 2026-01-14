from _typeshed import Incomplete
from gllm_docproc.model.element import Element as Element, HEADING as HEADING, PARAGRAPH as PARAGRAPH, TABLE as TABLE, TITLE as TITLE, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.parser.base_parser import BaseParser as BaseParser
from typing import Any

TABLE_AND_CAPTION_STRUCTURE: Incomplete
UPPER_ELEMENT_IS_CAPTION: str
LOWER_ELEMENT_IS_CAPTION: str
MAX_CAPTION_LENGTH: str
REMOVE_CAPTION_FROM_ELEMENT: str
MAX_CAPTION_ELEMENTS: str
UPPER_CAPTION_EXTRACTOR: str
LOWER_CAPTION_EXTRACTOR: str

def curry_upper_caption_extractor(remove_caption_from_element: bool):
    """Curry Upper Caption Extractor.

    This function curries the extract_upper_caption function with the remove_caption_from_element parameters.

    Why we need to use currying?
    1. so user can customize the upper_caption_extractor function
    2. the customize upper_caption_extractor may not require the remove_caption_from_element parameter

    Args:
        remove_caption_from_element (bool): A boolean value to remove the caption from the element.

    Returns:
        function: The function to extract the upper caption.
    """
def curry_lower_caption_extractor(remove_caption_from_element: bool):
    """Curry Lower Caption Extractor.

    This function curries the extract_lower_caption function with the remove_caption_from_element parameters.

    Why we need to use currying?
    1. so user can customize the lower_caption_extractor function
    2. the customize lower_caption_extractor may not require the remove_caption_from_element parameter

    Args:
        remove_caption_from_element (bool): A boolean value to remove the caption from the element.

    Returns:
        function: The function to extract the lower caption.
    """

class TableCaptionParser(BaseParser):
    """TableCaptionParser class.

    A class to extract table captions from a document and add them to the metadata of the table element.

    Methods:
        parse(loaded_elements, **kwargs): Extract table captions from a document and add them to
            the metadata of the table element.
    """
    def parse(self, loaded_elements: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Parses the elements to extract table captions.

        This method extracts table captions from the elements and adds them to the metadata of the table element.

        Args:
            loaded_elements (list[dict[str, Any]]): The elements to extract table captions from.
            **kwargs (Any): Additional keyword arguments for customization.

        Returns:
            list[dict[str, Any]]: The elements with the table captions added to the metadata.
        """
