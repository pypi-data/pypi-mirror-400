from _typeshed import Incomplete
from gllm_docproc.model.element import Element as Element
from gllm_docproc.model.media import MediaSourceType as MediaSourceType, MediaType as MediaType
from gllm_docproc.parser.base_parser import BaseParser as BaseParser
from typing import Any

SUPPORTED_TARGET_MIME_TYPES: Incomplete

class ImageMIMENormalizationParser(BaseParser):
    """Parser for normalizing unsupported image MIME types.

    This parser identifies images with unsupported MIME types and converts them to the target MIME type.
    """
    target_mime_type: Incomplete
    target_format: Incomplete
    supported_mime_types: Incomplete
    logger: Incomplete
    def __init__(self, target_mime_type: str = 'image/png', supported_mime_types: set[str] | None = None) -> None:
        '''Initialize the image MIME normalization parser.

        Args:
            target_mime_type (str, optional): The target MIME type to convert images to.
                Must be one of the supported target MIME types. Defaults to "image/png".
            supported_mime_types (set[str] | None, optional): Set of MIME types that don\'t need normalization.
                If None, only the target format is considered supported. Defaults to None.

        Raises:
            ValueError: If target_mime_type is not in SUPPORTED_TARGET_MIME_TYPES.
        '''
    def parse(self, loaded_elements: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Parse unsupported MIME type image to the target MIME type.

        This function will normalize the image base64 in element.media to the target mime type.
        If conversion fails, we will keep the original image base64 and the process will continue.

        Args:
            loaded_elements (list[dict[str, Any]]): A list of elements in list dict format where each dict
                mirroring the Element model structure
            **kwargs (Any): Additional keyword arguments.

        Returns:
            list[dict[str, Any]]: Elements with normalized images.
        """
