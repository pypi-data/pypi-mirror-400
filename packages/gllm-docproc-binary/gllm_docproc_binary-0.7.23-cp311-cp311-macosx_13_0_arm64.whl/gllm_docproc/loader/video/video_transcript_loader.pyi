from _typeshed import Incomplete
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import create_base_element_metadata as create_base_element_metadata
from gllm_docproc.loader.video.video_loader_utils import convert_video_to_audio_bytes as convert_video_to_audio_bytes, is_supported_video_file as is_supported_video_file
from gllm_docproc.model.element import Element as Element, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata, VIDEO as VIDEO
from gllm_docproc.utils import run_async_in_sync as run_async_in_sync
from gllm_multimodal.modality_converter.audio_to_text.audio_to_text import BaseAudioToText as BaseAudioToText
from gllm_multimodal.modality_converter.schema import AudioTranscript as AudioTranscript
from typing import Any

class VideoTranscriptLoader(BaseLoader):
    """Video Transcript Loader class for comprehensive video processing.

    This class provides a complete pipeline for processing video files by:
    - Converting video to audio using GStreamer (supports MP4, AVI, MOV, MKV, WebM, etc.)
    - Transcribing audio using configurable Audio-to-Text converters
    - Processing transcript elements with enhanced metadata
    - Converting structured elements to the GLLM format

    Attributes:
        audio_to_text_converters (list[BaseAudioToText]): List of audio transcription converters.
        logger (Logger): Logger instance for the class.
    """
    logger: Incomplete
    audio_to_text_converters: Incomplete
    def __init__(self, audio_to_text_converters: list[BaseAudioToText] | None = None) -> None:
        """Initialize the VideoTranscriptLoader class.

        Args:
            audio_to_text_converters (list[BaseAudioToText], optional): List of audio-to-text converters.
                Defaults to OpenAI Whisper if not provided.
        """
    def load(self, source: str, loaded_elements: Any = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load and process video file through the transcription pipeline.

        This method processes a video file by:
        1. Converting video to audio using GStreamer
        2. Transcribing audio to text using configured Audio-to-Text converters
        3. Converting transcripts to structured Element objects
        4. Returning elements as a list of dictionaries

        Supports any video format that GStreamer can handle (MP4, AVI, MOV, MKV, WebM, etc.).

        Args:
            source (str): Path to the video file.
            loaded_elements (Any): The loaded elements from previous loaders (not used in this implementation).
            **kwargs (Any): Additional keyword arguments (currently not used).

        Kwargs:
            original_source (str, optional): The original source of the document.

        Returns:
            list[dict[str, Any]]: List of video transcript elements as dictionaries.

        Raises:
            FileNotFoundError: If the video file doesn't exist.
            ValueError: If the file is not a supported video format or if conversion/transcription fails.
        """
