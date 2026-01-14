from enum import StrEnum

class LoaderType(StrEnum):
    """Loader Type Enum.

    This enum defines the different loader types.
    """
    AUDIO_LOADER: str
    CSV_LOADER: str
    DOCX_LOADER: str
    HTML_LOADER: str
    IMAGE_LOADER: str
    JSON_ELEMENTS_LOADER: str
    PDF_LOADER: str
    PPTX_LOADER: str
    TXT_LOADER: str
    VIDEO_LOADER: str
    XLSX_LOADER: str
    UNCATEGORIZED: str
    KEY: str
