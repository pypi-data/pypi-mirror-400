from gllm_docproc.model.element import PARAGRAPH as PARAGRAPH
from gllm_docproc.parser.base_parser import BaseParser as BaseParser
from gllm_docproc.utils.html_constants import HTMLTags as HTMLTags, ItemDataKeys as ItemDataKeys, Structure as Structure
from typing import Any

class HTMLFlatParser(BaseParser):
    """This class extends the BaseParser and is specifically designed for parsing elements loaded from web content.

    It assigns a structure to each loaded element based on the HTML tags present in its metadata.

    Attributes:
        None

    Methods:
        parse(loaded_elements: list[dict], **kwargs: dict[str, Any]) -> list[dict]:
            Parses the loaded_elements and assigns a structure to each element based on its HTML tags.
    """
    def parse(self, loaded_elements: list[dict[str, Any]], **kwargs: dict[str, Any]) -> list[dict[str, Any]]:
        """Parses the loaded_elements and assigns a structure to each element based on its HTML tags.

        Args:
            loaded_elements (list[dict]): The elements loaded from web content to be parsed.
            **kwargs (dict[str, Any]): Additional keyword arguments.

        Returns:
            list[dict]: The parsed elements with assigned structures.
        """
