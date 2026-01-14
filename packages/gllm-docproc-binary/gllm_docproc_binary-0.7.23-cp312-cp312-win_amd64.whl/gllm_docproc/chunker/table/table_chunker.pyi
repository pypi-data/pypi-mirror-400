from _typeshed import Incomplete
from gllm_docproc.chunker.base_chunker import BaseChunker as BaseChunker
from gllm_docproc.model.element import Element as Element, TABLE as TABLE
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata
from typing import Any

MARKDOWN: str
CSV: str
HTML: str

class TableChunker(BaseChunker):
    """Table Chunker class.

    This class is used to chunk a table element into smaller chunks. It implements the 'chunk' method
    to handle chunking the table element based on the chunk size and overlap. The table is converted
    into the expected format (markdown, csv, or html).

    Methods:
        chunk(elements, **kwargs): Chunk a table element into smaller chunks.
    """
    chunk_size: Incomplete
    chunk_overlap: Incomplete
    table_format: Incomplete
    table_splitter: Incomplete
    def __init__(self, chunk_size: int = 4000, chunk_overlap: int = 0, table_format: str = ...) -> None:
        """Initializes the TableChunker class.

        Args:
            chunk_size (int): The size of each chunk.
            chunk_overlap (int): The overlap between each chunk.
            table_format (str): The format of the table (markdown, csv, or html).
        """
    def chunk(self, elements: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Chunk a table element into smaller chunks.

        This method chunks a table element into smaller chunks based on the chunk size and overlap.
        It converts the table into the expected format (markdown, csv, or html) and then chunks the table.

        Args:
            elements (list[dict[str, Any]]): The table element to be chunked.
            **kwargs (Any): Additional keyword arguments for customization.

        Returns:
            list[dict[str, Any]]: The list of smaller chunks.
        """
