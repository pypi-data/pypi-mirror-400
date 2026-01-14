from _typeshed import Incomplete
from gllm_docproc.data_generator.base_data_generator import BaseDataGenerator as BaseDataGenerator
from gllm_docproc.model.element import Element as Element, PAGE as PAGE
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, IMAGE as IMAGE
from gllm_multimodal.modality_converter.image_to_text.image_to_caption.image_to_caption import BaseImageToCaption
from typing import Any

class ImageCaptionDataGenerator(BaseDataGenerator):
    """Data generator for creating captions from images using BaseImageToCaption."""
    DEFAULT_ELEMENT_PROCESSING_LIMIT: int
    image_to_caption: Incomplete
    def __init__(self, image_to_caption: BaseImageToCaption) -> None:
        """Initialize the ImageCaptionDataGenerator.

        Args:
            image_to_caption (BaseImageToCaption): The image to caption converter instance.
        """
    def generate(self, elements: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Generates captions by processing images in the input elements.

        Args:
            elements (list[dict[str, Any]]): List of dictionaries containing image data.
                Each dictionary should have an 'image_source' key with the image location.
            **kwargs (Any): Additional keyword arguments for the image captioning process.

        Kwargs:
            image_format_func (Callable[[str, Element], str], optional): Function to format the caption text.
                Defaults to None.
            element_processing_limit (int, optional): The maximum number of elements to process at a time.
                Defaults to 100.
            use_image_text_as_context (bool, optional): Whether to use the image text as context.
                If set to False, will use `image_description` instead. Defaults to False.

        Returns:
            list[dict[str, Any]]: List of dictionaries containing the processed image data.
                Each dictionary will contain the original data.

        Raises:
            ValueError: If elements don't contain required image information.
        """
