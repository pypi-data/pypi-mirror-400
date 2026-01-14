from enum import StrEnum
from pydantic import BaseModel, computed_field

class MediaType(StrEnum):
    """Defines valid media types."""
    IMAGE: str
    AUDIO: str
    VIDEO: str
    YOUTUBE: str

class MediaSourceType(StrEnum):
    """Defines valid media source types."""
    BASE64: str
    URL: str

class Media(BaseModel):
    """Media model which contains media information.

    This class serves as the base model for storing media information in element metadata.
    Element with media (image, audio, video, youtube) will have metadata `media` in list of dict.
    Each dict will be following the Media model schema.

    Attributes:
        media_id (str): Unique identifier for the media, automatically generated from media_type and media_content.
        media_type (MediaType): Type of media (image, audio, video, youtube).
        media_content (str): Base64 encoded string or URL pointing to the media content.
        media_content_type (MediaSourceType): Type of content source (base64 or url).
    """
    media_type: MediaType
    media_content: str
    media_content_type: MediaSourceType
    @computed_field
    @property
    def media_id(self) -> str:
        """Generate a standardized media ID.

        This property generates a standardized media ID in the format:
        {media_type}_{sha256_from_media_content_16_digit}

        Returns:
            str: The generated media ID.
        """
    class Config:
        """Pydantic model configuration.

        This class defines the Pydantic model configuration for the Media model.

        Attributes:
            extra (str): Allow extra fields.
        """
        extra: str
