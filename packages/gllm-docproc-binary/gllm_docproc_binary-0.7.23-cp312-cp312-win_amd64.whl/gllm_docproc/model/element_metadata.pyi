from pydantic import BaseModel

PDF: str
DOCX: str
XLSX: str
PPTX: str
CSV: str
TXT: str
HTML: str
AUDIO: str
IMAGE: str
VIDEO: str

class ElementMetadata(BaseModel):
    """Element metadata model.

    This class serves as the Element metadata model for storing element metadata.

    Mandatory Attributes:
        source (str): The source of the element.
        source_type (str): The source type of the element.
        loaded_datetime (datetime): The datetime when the element is loaded.
    """
    source: str
    source_type: str
    loaded_datetime: str
    class Config:
        """Pydantic model configuration.

        This class defines the Pydantic model configuration for the ElementMetadata model.

        Attributes:
            extra (str): Allow extra fields.
        """
        extra: str
