from _typeshed import Incomplete
from gllm_docproc.chunker.base_chunker import BaseChunker as BaseChunker
from gllm_docproc.chunker.structured_element.chunk_enricher import enrich_chunk as enrich_chunk
from gllm_docproc.chunker.table import TableChunker as TableChunker
from gllm_docproc.model.element import AUDIO as AUDIO, Element as Element, FOOTER as FOOTER, FOOTNOTE as FOOTNOTE, HEADER as HEADER, HEADING as HEADING, IMAGE as IMAGE, PAGE as PAGE, TABLE as TABLE, TITLE as TITLE, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT, VIDEO as VIDEO
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Any

NON_TEXT_STRUCTURE: Incomplete

def default_text_splitter() -> RecursiveCharacterTextSplitter:
    '''Define the default text splitter for structured text chunking.

    This function defines the default text splitter for structured text chunking.
    The text splitter is defined with the following separators:

        1. "\\n#" : Split by Title or Heading
        2. "\\n\\n" : Split between Paragraph Elements
        3. "\\n" : Split between Title/Heading and Paragraph Elements
        4. ". " | "! " | "? " : Split by Sentence
        5. ", " : Split by Word
        6. " " : Split by Word
        7. "" : Split by Character

    Returns:
        RecursiveCharacterTextSplitter: A RecursiveCharacterTextSplitter object for structured text chunking.
    '''

class StructuredElementChunker(BaseChunker):
    """A class for structured text chunker.

    This class defines the structure for chunking structured text into smaller chunks. It implements
    the 'chunk' method to handle structured text chunking.

    Methods:
        chunk(elements, **kwargs): Chunk the structured text into smaller chunks.
    """
    default_text_splitter: Incomplete
    default_table_chunker: Incomplete
    text_splitter: Incomplete
    table_chunker: Incomplete
    is_parent_structure_info_included: Incomplete
    def __init__(self, text_splitter: RecursiveCharacterTextSplitter = ..., table_chunker: BaseChunker = ..., is_parent_structure_info_included: bool = True) -> None:
        """Initialize the structured text chunker.

        Args:
            text_splitter (RecursiveCharacterTextSplitter): A RecursiveCharacterTextSplitter object
                for structured text chunking.
            table_chunker (BaseChunker): A BaseChunker object for table chunking.
            is_parent_structure_info_included (bool): A boolean value to include parent structure
                information in the chunk.
        """
    def chunk(self, elements: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        '''Chunk the structured text into smaller chunks.

        This method defines the process of chunking structured text into smaller chunks. It uses the
        RecursiveCharacterTextSplitter to split the text into chunks based on the defined separators.

        The method will split the text recursively based on the defined separators, or by default:
            1. "\\n#" : Split by Title or Heading
            2. "\\n\\n" : Split between Paragraph Elements
            3. "\\n" : Split between Title/Heading and Paragraph Elements
            4. ". " | "! " | "? " : Split by Sentence
            5. ", " : Split by Word
            6. " " : Split by Word
            7. "" : Split by Character

        Kwargs:
            excluded_structures (list[str]): A list of structures to be excluded from the chunking process.
            enrich_chunk (Callable[[Element, list[Element]], Element]): A function to enrich the chunked element.
            file_id (str | None): The file id of the chunked elements. Defaults to None.

        Args:
            elements (list[dict[str, any]]): A list of dictionaries containing text and structure.
            **kwargs (Any): Additional keyword arguments for the chunker.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing chunked text and metadata.
        '''
