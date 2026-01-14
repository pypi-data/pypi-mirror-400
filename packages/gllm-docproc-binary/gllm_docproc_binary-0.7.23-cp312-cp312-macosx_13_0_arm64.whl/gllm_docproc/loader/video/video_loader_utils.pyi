import numpy as np
from _typeshed import Incomplete
from gllm_docproc.loader.exception import VideoConversionError as VideoConversionError

logger: Incomplete
DEFAULT_SAMPLE_RATE: int
AUDIO_NORMALIZATION_FACTOR: float
PCM_16_MAX_VALUE: int
INT16_TO_FLOAT_DIVISOR: float
GSTREAMER_MAX_BUFFERS: int

def is_supported_video_file(file_path: str) -> bool:
    """Validate if a file is a supported video format using intelligent MIME detection.

    Args:
        file_path (str): Absolute or relative path to the file to validate.

    Returns:
        bool: True if the file is a supported video format, False otherwise.
    """
def convert_video_to_audio_bytes(video_path: str, target_sample_rate: int | None = ..., normalize_audio: bool = True, audio_format: str = 'WAV', audio_subtype: str | None = None) -> bytes:
    '''Convert video file to audio bytes optimized for audio transcription services using GStreamer.

    This function provides a complete video-to-audio processing pipeline that:
    1. Extracts audio from video using GStreamer
    2. Processes and normalizes the audio signal
    3. Resamples to target sample rate (optional)
    4. Encodes to specified audio format with intelligent defaults
    5. Returns audio bytes ready for transcription services or file output

    Args:
        video_path (str): Path to the input video file.

        target_sample_rate (int | None, optional): Target sample rate for the audio output.
            Common values:
            - 16000 Hz: Optimal for speech recognition (default)
            - 44100 Hz: CD quality, good for music transcription
            - 48000 Hz: Professional audio standard
            - None: Preserve original video\'s sample rate

            Higher sample rates provide better quality but larger file sizes.
            Most transcription services work best with 16kHz. Defaults to 16000.

        normalize_audio (bool, optional): Whether to normalize audio amplitude.
            Set to False if the transcription service handles its own normalization. Defaults to True.

        audio_format (str, optional): Target audio format for the output. Case-insensitive.
            **Recommended formats for transcription:**
            - "WAV": Uncompressed, maximum compatibility (default)

            See `audio_to_bytes()` documentation for complete format list.
            Defaults to "WAV".

        audio_subtype (str | None, optional): Audio encoding subtype.
            If None, uses format defaults: WAV→"PCM_16", FLAC→"PCM_16", MP3→"MPEG_LAYER_III", OGG→"VORBIS".
            Common options: "PCM_16", "PCM_24", "PCM_32", "FLOAT".
            Defaults to None.

    Returns:
        bytes: Audio data in the specified format, ready for transcription services or file output.

    Raises:
        FileNotFoundError: If the video file doesn\'t exist.
        ValueError: If unsupported format, no audio stream, or invalid format-subtype combination.
        VideoConversionError: For other conversion failures (decoding, processing, encoding errors).

    Examples:
        >>> audio_bytes = convert_video_to_audio_bytes("meeting.mp4")  # Default: WAV, 16kHz
        >>> audio_bytes = convert_video_to_audio_bytes("concert.mov", target_sample_rate=44100, audio_format="FLAC")
        >>> audio_bytes = convert_video_to_audio_bytes("lecture.avi", audio_format="MP3")  # Smaller files
    '''
def audio_to_bytes(audio_data: np.ndarray, sample_rate: int, audio_format: str = 'WAV', subtype: str | None = None) -> bytes:
    '''Convert audio data to specified format bytes.

    Args:
        audio_data (np.ndarray): Audio data as NumPy array.
        sample_rate (int): Sample rate in Hz (e.g., 16000, 44100).
        audio_format (str, optional): Target format. Supports WAV, FLAC, MP3, OGG, AIFF, etc.
            See `soundfile.available_formats()` for the complete list.
            Defaults to "WAV".
        subtype (str | None, optional): Audio encoding subtype.
            If None, uses soundfile\'s format defaults: WAV→"PCM_16", FLAC→"PCM_16", MP3→"MPEG_LAYER_III", OGG→"VORBIS".
            See `soundfile.available_subtypes(format)` for the complete list.
            Defaults to None.

    Returns:
        bytes: Audio data in the specified format.

    Raises:
        ValueError: If unsupported format/subtype or incompatible format-subtype combination.

    Examples:
        >>> audio_data = np.array([0.1, -0.2, 0.3], dtype=np.float32)
        >>> wav_bytes = audio_to_bytes(audio_data, 16000)  # WAV + PCM_16
        >>> flac_bytes = audio_to_bytes(audio_data, 44100, "FLAC")  # FLAC + PCM_16
        >>> mp3_bytes = audio_to_bytes(audio_data, 16000, "MP3")  # MP3 + MPEG_LAYER_III
    '''
