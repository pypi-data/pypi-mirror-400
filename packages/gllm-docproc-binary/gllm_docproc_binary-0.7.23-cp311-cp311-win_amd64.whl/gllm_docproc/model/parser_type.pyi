from enum import StrEnum

class ParserType(StrEnum):
    """Parser Type Enum.

    This enum defines the different parser types.
    """
    AUDIO_PARSER: str
    CSV_PARSER: str
    DOCX_PARSER: str
    HTML_PARSER: str
    IMAGE_PARSER: str
    PDF_PARSER: str
    PPTX_PARSER: str
    TXT_PARSER: str
    VIDEO_PARSER: str
    XLSX_PARSER: str
    UNCATEGORIZED: str
    KEY: str
