from gllm_docproc.model.element import Element as Element, FOOTER as FOOTER, FOOTNOTE as FOOTNOTE, HEADER as HEADER, HEADING as HEADING, PARAGRAPH as PARAGRAPH, TITLE as TITLE, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.parser.base_parser import BaseParser as BaseParser
from typing import Any

HEADER_THRESHOLD_POSITION: int
FOOTER_THRESHOLD_POSITION: int
FOOTNOTE_POSITION_RATIO: float

class PDFParser(BaseParser):
    """A class to parse PDF documents.

    This class serves as a PDF parser for parsing or defining the structure of text within PDF documents
    based on the text metadata (font size, font family, coordinates, etc.).

    Methods:
        parse: Parse the loaded elements.
    """
    def parse(self, loaded_elements: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Parse the loaded elements.

        This method defines the process of defining text structure of the loaded elements based on metadata
        for PDF loaded elements.

        Args:
            loaded_elements (list[dict[str, Any]]): A list of dictionaries containing loaded element
                content and metadata.
            **kwargs (Any): Additional keyword arguments.

        Kwargs:
            header_footer_tolerance (int, optional): An integer value indicating the tolerance for header and footer.
                Defaults to 0.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing parsed element content and metadata.
        """
