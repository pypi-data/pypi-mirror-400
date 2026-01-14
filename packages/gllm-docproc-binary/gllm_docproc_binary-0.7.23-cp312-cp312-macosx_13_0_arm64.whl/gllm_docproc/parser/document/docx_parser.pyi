from gllm_docproc.model.element import Element as Element, FOOTER as FOOTER, HEADER as HEADER, HEADING as HEADING, MAX_HEADING_LEVEL as MAX_HEADING_LEVEL, PARAGRAPH as PARAGRAPH, TITLE as TITLE, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.parser.base_parser import BaseParser as BaseParser
from typing import Any

class DOCXParser(BaseParser):
    """A DOCX parser for parsing DOCX document text structure.

    This class serves as the DOCX parser for parsing DOCX document text structure.
    It defines the structure for parsing DOCX document text structure from a given loaded_elements.

    Methods:
        parse(loaded_elements, **kwargs): Parse the document from the loaded elements.
    """
    def parse(self, loaded_elements: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Parse the document from the loaded elements.

        This method defines the process of defining text structure from loaded_elements (DOCX Loader output)
        by their style_name. In cases there's customized style_name, it will be categorized as paragraph.
        (example: 'Heading', 'Heading Body', 'Title 1', will be categorized as paragraph.)

        Args:
            loaded_elements (list[dict[str, Any]]): A list of loaded elements containing text content and metadata.
            **kwargs (Any): Additional keyword arguments for parsing the document.

        Returns:
            list[dict[str, Any]]: A list of parsed elements containing text content and metadata.
        """
