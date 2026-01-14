from gllm_docproc.model.element import Element as Element, PARAGRAPH as PARAGRAPH, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.parser.base_parser import BaseParser as BaseParser
from typing import Any

class TXTParser(BaseParser):
    """TXT parser for parsing text files.

    Methods:
        parse: Parse a list of elements from a text file.
    """
    def parse(self, loaded_elements: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Parse a list of elements from a text file.

        all elements with structure UNCATEGORIZED_TEXT will be converted to PARAGRAPH

        Args:
            loaded_elements (list[dict[str, Any]]): The list of elements that have already been loaded.
            **kwargs: Additional keyword arguments.

        Returns:
            list[dict[str, Any]]: A list of elements.
        """
