from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.docx.python_docx_loader import PythonDOCXLoader as PythonDOCXLoader
from gllm_docproc.model.element import Element as Element, TABLE as TABLE
from typing import Any

class PythonDOCXTableLoader(BaseLoader):
    """Python DOCX Table Loader class to load tables from DOCX document.

    This class is used to load tables from DOCX document using python-docx library.
    Then it combined the existing loaded elements with the loaded tables.

    Methods:
        load: Load the tables from the DOCX document and combine it with the existing loaded elements.
        _filter_table_elements: Filter the table elements from the loaded elements.
        _get_table_content_count: Get the table content count.
        _is_table_match: Is the table match with the merged table.
        _find_matching_merged_table: Find the matching merged table.
    """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load the tables from the DOCX document and combine it with the existing loaded elements.

        This function loads the tables from the DOCX document using python-docx library.
        Then it combined the existing loaded elements with the loaded tables.

        Args:
            source (str): The source file path.
            loaded_elements (list[dict[str, Any]] | None): The existing loaded elements.
            **kwargs (Any): The keyword arguments.

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: The loaded elements.
        """
