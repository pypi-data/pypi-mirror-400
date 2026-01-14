from gllm_docproc.model.element import Element as Element
from gllm_docproc.parser import BaseParser as BaseParser
from typing import Any

DEFAULT_SHEET_NAME_PATTERN: str

class XLSXParser(BaseParser):
    """A XLSX parser for parsing XLSX document text structure.

    This class serves as the XLSX parser for parsing XLSX document text structure.
    It defines the structure for parsing XLSX document text structure from a given loaded_elements.

    Methods:
        parse(loaded_elements, **kwargs): Parse the document from the loaded elements.
    """
    def parse(self, loaded_elements: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Parse loaded elements by assigning a structure to each element.

        Args:
            loaded_elements (list[dict[str, Any]]): A list of dictionaries representing loaded elements.
            **kwargs (Any): Additional arguments for parsing the document.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing parsed elements with assigned structures.

        """
