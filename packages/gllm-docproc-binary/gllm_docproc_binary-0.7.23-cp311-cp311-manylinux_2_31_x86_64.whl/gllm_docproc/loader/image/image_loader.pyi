from _typeshed import Incomplete
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata
from gllm_docproc.model.element import Element as Element, IMAGE as IMAGE
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata
from gllm_docproc.model.media import Media as Media, MediaSourceType as MediaSourceType, MediaType as MediaType
from typing import Any

class ImageLoader(BaseLoader):
    """A class for loading standalone image files.

    This class defines the structure for loading standalone image files.
    It supports all image formats by validating that the MIME type starts with 'image/'.

    Methods:
        load: Load an image file into a list of elements.
        is_image_file: Check if a file is a valid image file based on the mime type.
    """
    logger: Incomplete
    def __init__(self) -> None:
        """Initialize the ImageLoader class."""
    def load(self, source: str, loaded_elements: list[dict[str, Any]] | None = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load an image file into a list of elements.

        This method loads an image file and creates Element objects with media metadata containing the image data.
        For multi-page images, each page/frame is extracted as a separate element.

        Args:
            source (str): The path to the image file.
            loaded_elements (list[dict[str, Any]] | None, optional): A list of elements that have already been loaded.
            **kwargs (Any): Additional keyword arguments for the loader.

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: A list of elements containing the image data.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not a valid image file.
        """
    def is_image_file(self, source: str) -> bool:
        """Check if a file is a valid image file.

        This method uses the `magic` library to check if a file is a valid image file
        by examining its MIME type. Any file with a MIME type starting with 'image/' is considered valid.

        Args:
            source (str): The path to the file.

        Returns:
            bool: True if the file is a valid image file, False otherwise.
        """
