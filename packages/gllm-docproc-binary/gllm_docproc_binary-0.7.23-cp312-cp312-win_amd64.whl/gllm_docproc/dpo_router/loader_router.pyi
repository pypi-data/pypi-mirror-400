from _typeshed import Incomplete
from gllm_docproc.dpo_router.base_dpo_router import BaseDPORouter as BaseDPORouter
from gllm_docproc.loader.csv.pandas_loader import CSV_VARIANTS as CSV_VARIANTS
from gllm_docproc.loader.image import ImageLoader as ImageLoader
from gllm_docproc.loader.json.json_elements_loader import JSON as JSON
from gllm_docproc.loader.txt import TXTLoader as TXTLoader
from gllm_docproc.loader.video.video_loader_utils import is_supported_video_file as is_supported_video_file
from gllm_docproc.model import Element as Element, LoaderType as LoaderType
from gllm_docproc.model.element_metadata import DOCX as DOCX, HTML as HTML, PDF as PDF, PPTX as PPTX, XLSX as XLSX
from typing import Any

class LoaderRouter(BaseDPORouter):
    """Loader Router class.

    This router determines the appropriate loader type based on the input source.
    Returns a dict with the loader type information.
    """
    logger: Incomplete
    txt_loader: Incomplete
    image_loader: Incomplete
    def __init__(self) -> None:
        """Initialize the LoaderRouter.

        This method initializes the LoaderRouter.
        """
    def route(self, source: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Route the input source to the appropriate loader type.

        This method determines the appropriate loader type based on the input source.
        It checks if the source is a file or a YouTube URL.
        1. If it is a file, it checks the file extension or content to determine the loader type.
        2. If it is a YouTube URL, it returns the audio loader type.
        3. If it is not a file or a YouTube URL, it returns the uncategorized loader type.

        Args:
            source (str): The input source, either a file path or a YouTube URL.
            *args (Any): Additional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            dict[str, Any]: A dictionary containing the loader type information.
                Example: {LoaderType.KEY: LoaderType.PDF_LOADER}
        """
    def is_html_from_json(self, source: str) -> bool:
        """Check if the source file contains valid HTML metadata.

        Args:
            source (str): The file path to check.

        Returns:
            bool: True if the file is a valid HTML metadata file, False otherwise.
        """
