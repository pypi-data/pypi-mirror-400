from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata, trim_table_empty_cells as trim_table_empty_cells, validate_file_extension as validate_file_extension
from gllm_docproc.loader.pdf.pdf_loader_utils import merge_loaded_elements_by_coordinates as merge_loaded_elements_by_coordinates
from gllm_docproc.loader.pdf.pdf_miner_word_loader import PDFMinerWordLoader as PDFMinerWordLoader
from gllm_docproc.model.element import Element as Element, TABLE as TABLE
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, PDF as PDF
from typing import Any

class TextInjectPDFPlumberLoader(BaseLoader):
    """A class for loading PDF documents using PDFPlumber by injecting text into tables.

    This class defines the structure for loading PDF documents using PDFPlumber by injecting text into tables.
    It implements the 'load' method to handle PDF loading from a given file path.

    TextInjectPDFPlumberLoader is used to extract the TABLE from the PDF document.

    Methods:
        load(source, loaded_elements, **kwargs): Load a PDF document.
    """
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load a PDF document.

        This method loads a PDF document from a given file path.

        Args:
            source (str): The file path of the PDF document.
            loaded_elements (list[dict[str, Any]]): The loaded elements.
            kwargs (Any): Additional keyword arguments.

        Kwargs:
            original_source (str, optional): The original source of the document.
            font_size_threshold (int, optional): The font size threshold. Defaults to None.
                When None, the font size threshold will be most frequent font size multiplied by 2.

        Returns:
            list[dict[str, Any]]: The loaded elements.
        """
