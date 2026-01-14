from gllm_docproc.parser.base_parser import BaseParser as BaseParser
from typing import Any

class PipelineParser:
    """Pipeline parser for parsing documents.

    This class serves as the pipeline parser for parsing documents. It defines the structure for
    parsing documents with several parsers using pipeline.

    Methods:
        add_parser(parser): Add parser to the pipeline parser.
        parse(elements, **kwargs): Parse the elements using parsers.
    """
    parsers: list[BaseParser]
    def __init__(self) -> None:
        """Initialize the pipeline parser."""
    def add_parser(self, parser: BaseParser):
        """Add parser to the pipeline parser.

        This method defines the process of adding parser to the pipeline parser.

        Args:
            parser (BaseParser): The parser to be added.
        """
    def parse(self, elements: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Parse the elements using pipeline parser.

        This method defines the process of parsing the elements using parsers.

        Args:
            elements (list[dict[str, Any]]): A list of dictionaries containing elements.
            **kwargs (Any): Additional keyword arguments.
        """
