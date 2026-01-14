from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from gllm_docproc.loader.loader_utils import validate_file_extension as validate_file_extension
from gllm_docproc.model.element import Element as Element
from typing import Any

JSON: str

class JSONElementsLoader(BaseLoader):
    """JSON Elements Loader class.

    This class provides a loader for extracting information from JSON files.
    The JSON file must be in the format of list of dictionaries. where each dictionary
    must be following the structure of Element class.

    Methods:
        load(source, element_metadata, **kwargs): Load and process a document.
    """
    def load(self, source: str, loaded_elements: Any = None, **kwargs: Any) -> list[dict[str, Any]]:
        """Load and process a document.

        This method loads the JSON file and returns the list of elements. If file id is provided,
        the file id will be added to the element metadata and the chunk id and chunk relation metadata
        that contains file id as prefix will be updated.

        Args:
            source (str): The file path of the JSON file.
            loaded_elements (Any, optional): The loaded elements. JSON Loader ignore this parameter.
            **kwargs (Any): The keyword arguments.

        Kwargs:
            file_id (str, optional): The file id of for the elements. Defaults to None.

        Returns:
            list[dict[str, Any]]: The loaded elements.
        """
