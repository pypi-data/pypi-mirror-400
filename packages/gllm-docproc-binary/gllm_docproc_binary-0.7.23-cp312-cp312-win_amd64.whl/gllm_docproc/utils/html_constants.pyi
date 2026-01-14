from _typeshed import Incomplete
from gllm_docproc.model.element import AUDIO as AUDIO, FOOTER as FOOTER, HEADER as HEADER, HEADING as HEADING, IMAGE as IMAGE, TABLE as TABLE, TITLE as TITLE, VIDEO as VIDEO

FORMATTING_TAGS: Incomplete
SPACING: str

class MetaDataKeys:
    """Represents keys commonly used in metadata for web content."""
    CHARSET: str
    PROPERTY: str
    CONTENT: str
    NAME: str
    HTTP_EQUIV: str
    URL: str
    TITLE: str
    METADATA: str
    SOURCE: str
    SOURCE_TYPE: str
    LOADED_DATETIME: str

class ContentDataKeys:
    """Represents keys commonly used in web content data."""
    TAG: str
    CONTENT: str
    SOURCE: str
    TYPE: str
    SRC: str
    PLACEHOLDER: str
    TABLE: str
    HREF: str
    ALT: str
    CLASS: str
    VALUE: str

class ItemDataKeys:
    """Represents keys used for handling item data."""
    ELEMENTS: str
    TEXT: str
    STRUCTURE: str
    ELEMENT_ID: str
    INDEX: str
    LINK: str
    FORMATS: str
    COMBINE_PREV: str
    LIST_TYPE: str
    IS_LIST_FIRST_ITEM: str
    METADATA: str
    URL: str
    GROUP_ID: str
    PARENT_ID: str
    LINE_BREAK: str
    HTML_TAGS: str
    ROW_ITEM: str
    COLSPAN: str
    ROWSPAN: str

class HTMLTags:
    """Represents commonly used HTML tags as constants."""
    IMG: str
    INPUT: str
    SVG: str
    SOURCE: str
    TABLE: str
    A: str
    VIDEO: str
    AUDIO: str
    IFRAME: str
    EMBED: str
    TEXT: str
    UL: str
    OL: str
    LI: str
    P: str
    BR: str
    H: Incomplete
    HEADER: str
    TITLE: str
    FOOTER: str
    MEDIA_TAGS: Incomplete
    TR: str
    TD: str
    TH: str
    TBODY: str
    TFOOT: str
    THEAD: str
    IMAGE_TAGS: Incomplete

class ErrorMessage:
    """Represents predefined error messages used in the application."""
    ERROR_FAILED_SAVE_JSON: str
    ERROR_FAILED_SAVE_CSV: str
    ERROR_FAILED_EXTRACT_DATA: str
    ERROR_MISSING_KEY: str
    ERROR_FAILED_TO_PROCESS_ITEM: str
    ERROR_FAILED_TO_OPEN_SPIDER: str
    ERROR_UNKNOWN_SOURCE: str

class Structure:
    """Represents the structure of the content."""
    @classmethod
    def get_structure(cls, tag: str):
        """Get the structure associated with the given HTML tag.

        This class method maps HTML tags to their corresponding structure types and returns the
        structure associated with the provided HTML tag.

        Args:
            tag (str): The HTML tag for which to retrieve the structure.

        Returns:
            str or None: The structure associated with the HTML tag, or None if the tag is not mapped.
        """

class TableConstants:
    """Represents constants used for table extraction."""
    TABLE_META_KEY: str
    TABLE_CONTENT_KEY: str
    TABLE_ROW_TYPE_KEY: str
    MAX_CHAR_COUNT_PER_COLUMN: str
    HEADER: str
    BODY: str
    FOOTER: str
