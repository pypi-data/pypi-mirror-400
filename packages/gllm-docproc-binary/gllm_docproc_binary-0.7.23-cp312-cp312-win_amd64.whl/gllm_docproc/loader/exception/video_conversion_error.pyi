from _typeshed import Incomplete

class VideoConversionError(Exception):
    """An exception for video conversion failures."""
    message: Incomplete
    def __init__(self, video_path: str, cause: str) -> None:
        """Initialize the exception.

        Args:
            video_path (str): Path to the video file that failed to convert.
            cause (str): Description of the underlying cause of the failure.
        """
