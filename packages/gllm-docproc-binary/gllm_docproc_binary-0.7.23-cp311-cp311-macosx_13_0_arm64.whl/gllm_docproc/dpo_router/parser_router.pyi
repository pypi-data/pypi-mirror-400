from _typeshed import Incomplete
from gllm_docproc.dpo_router.base_dpo_router import BaseDPORouter as BaseDPORouter
from gllm_docproc.model.element import Element as Element
from gllm_docproc.model.element_metadata import AUDIO as AUDIO, CSV as CSV, DOCX as DOCX, HTML as HTML, IMAGE as IMAGE, PDF as PDF, PPTX as PPTX, TXT as TXT, VIDEO as VIDEO, XLSX as XLSX
from gllm_docproc.model.parser_type import ParserType as ParserType
from typing import Any

class ParserRouter(BaseDPORouter):
    """Parser Router class.

    This router determines the appropriate parser type based on the input source.
    Returns a dict with the parser type information.
    """
    logger: Incomplete
    source_type_to_parser_type: Incomplete
    def __init__(self) -> None:
        """Initialize the ParserRouter.

        This method initializes the ParserRouter.
        """
    def route(self, source: str | list[dict[str, Any]], *args, **kwargs) -> dict[str, Any]:
        """Determine the parser type from the input source.

        The input source can be:
        - A string path to a JSON file containing loaded elements.
        - A list of loaded element dictionaries (in memory).

        This method reads the input, extracts the `source_type` from the first element’s metadata,
        and returns the appropriate parser type. If loading fails or metadata is missing,
        the parser type will be set as UNCATEGORIZED.

        Args:
            source (str | list[dict[str, Any]]): The input source, which can be either:
                - str: path to a JSON file containing loaded elements.
                - list[dict[str, Any]]: loaded elements.
            *args (Any): Additional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            dict[str, Any]: A dictionary containing the parser type information.
                Example: {ParserType.KEY: ParserType.PDF_PARSER}
        """
