from gllm_docproc.model.element import Element as Element
from gllm_docproc.parser.base_parser import BaseParser as BaseParser
from gllm_docproc.parser.html.nested.html_json_processor import HTMLJsonProcessor as HTMLJsonProcessor
from typing import Any

class HTMLNestedParser(BaseParser):
    """A parser class for processing JSON elements into a parsed elements.

    This class inherits from the BaseParser class and implements the parse method
    to convert loaded HTML elements into a processed JSON format.

    Attributes:
        None
    """
    def parse(self, loaded_elements: list[dict[str, Any]], **kwargs: dict[str, Any]) -> list[dict[str, Any]]:
        """Processes loaded HTML elements into a JSON format.

        Args:
            loaded_elements (dict): The loaded HTML elements to be processed.
            **kwargs (dict[str, Any]): Additional keyword arguments.

        Returns:
            dict: The processed JSON representation of the HTML elements.
        """
