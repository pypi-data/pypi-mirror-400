from _typeshed import Incomplete
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata
from gllm_docproc.model.element import Element as Element, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.model.element_metadata import AUDIO as AUDIO, ElementMetadata as ElementMetadata
from gllm_multimodal.modality_converter.audio_to_text.audio_to_text import BaseAudioToText as BaseAudioToText
from gllm_multimodal.modality_converter.schema import AudioTranscript as AudioTranscript
from typing import Any

class AudioLoader(BaseLoader):
    """Audio Loader class.

    This class provides a loader for audio files for extracting information from audio files
    using GLLM Multimodal Audio to Text. It implements the 'load' method to handle document loading
    from a given source.

    Attributes:
        audio_to_text_converters (list[BaseAudioToText]): A list of audio to text converter from GLLM Multimodal.
    """
    audio_to_text_converters: Incomplete
    logger: Incomplete
    def __init__(self, audio_to_text_converters: list[BaseAudioToText] | None = None) -> None:
        """Initialize the AudioLoader class.

        Args:
            audio_to_text_converters (list[BaseAudioToText] | None): A list of audio to text converters.
                If None, defaults to using YouTubeTranscriptAudioToText and OpenAIWhisperAudioToText.
        """
    def load(self, source: str, loaded_elements: Any = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load and process audio file using the GLLM Multimodal Audio to Text.

        This method will transcribe the audio file using the GLLM Multimodal Audio to Text. It will then convert the
        transcription results to elements.

        Args:
            source (str): The source of the audio file to be transcribed.
            loaded_elements (Any): The loaded elements to be processed.
            **kwargs (Any): Additional keyword arguments for the loader

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: The loaded elements.
        """
