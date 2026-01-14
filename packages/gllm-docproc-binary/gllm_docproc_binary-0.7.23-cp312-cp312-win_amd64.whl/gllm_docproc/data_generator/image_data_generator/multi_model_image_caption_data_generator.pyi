from _typeshed import Incomplete
from gllm_docproc.data_generator.base_data_generator import BaseDataGenerator as BaseDataGenerator
from gllm_docproc.data_generator.image_data_generator.image_caption_data_generator import ImageCaptionDataGenerator as ImageCaptionDataGenerator
from gllm_docproc.model.element import IMAGE as IMAGE
from typing import Any

DEFAULT_MODEL_ID: str

class MultiModelImageCaptionDataGenerator(BaseDataGenerator):
    """Multi-model image captioning data generator with lazy initialization.

    This class extends BaseDataGenerator to provide a data generator for image captioning that supports multiple models
    with lazy initialization, to avoid API key validation during pipeline initialization.

    Key Features:
    1. Supports multiple models in a single instance.
    2. Lazy initialization to avoid API key validation during initialization.
    3. Dynamic model selection at runtime.
    """
    model_api_keys: Incomplete
    logger: Incomplete
    def __init__(self, model_api_keys: dict[str, str] | None = None) -> None:
        """Initialize the MultiModelImageCaptionDataGenerator.

        Args:
            model_api_keys (dict[str, str] | None, optional): Dictionary mapping model IDs to their API keys.
                Defaults to None, in which case no API keys passed during LMInvoker initialization.
        """
    def generate(self, elements: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        '''Generate captions for elements with image structure.

        Args:
            elements (list[dict[str, Any]]): List of dictionaries containing elements to be processed.
            **kwargs (Any): Additional keyword arguments for the image captioning process.

        Kwargs:
            model_id (str, optional): The ID of the model to use for image captioning.
                Defaults to DEFAULT_MODEL_ID which is using the "google/gemini-2.5-flash".
            system_prompt (str, optional): The system prompt to use for image captioning.
                Defaults to DEFAULT_SYSTEM_PROMPT.
            user_prompt (str, optional): The user prompt to use for image captioning.
                Defaults to DEFAULT_USER_PROMPT.
            default_hyperparameters (dict[str, Any]): Additional hyperparameters passed to
                the LMInvoker configuration. Defaults to {}.
            retry_config (dict[str, Any], optional): The retry config to use for the LM invoker.
                If not provided, will use the default retry config. Defaults to {}.

        Returns:
            list[dict[str, Any]]: List of dictionaries containing the processed image data.
                Each dictionary will contain the original data.
        '''
