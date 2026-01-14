from gllm_docproc.loader.exception import UnsupportedFileExtensionError as UnsupportedFileExtensionError
from gllm_docproc.model.element_metadata import ElementMetadata as ElementMetadata

def validate_file_extension(expected_extensions: str | list[str], loader_name: str):
    """Decorator to validate the file extension of the input file.

    Args:
        expected_extensions (str | list[str]): The expected file extension(s). Can be a single extension
            as a string or a list of valid extensions. Extensions are case-insensitive.
        loader_name (str): The name of the loader.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]: A decorator that wraps the original
            function to validate the file extension.

    Raises:
        UnsupportedFileExtensionError: If the file extension does not match the expected extension.
    """
def create_base_element_metadata(source: str, source_type: str) -> ElementMetadata:
    """Create the base element metadata.

    This function creates the base element metadata for the loaded element. Base element metadata
    includes the source, source type, and loaded datetime.

    Args:
        source (str): The source of the element.
        source_type (str): The source type.

    Returns:
        ElementMetadata: The base element metadata.
    """
def trim_table_empty_cells(table: list[list[str]]) -> list[list[str]]:
    """Trim the empty cells in the table.

    This function trims the empty cells in the table by removing the empty cells at the end of each
    row. The function also ensures that all rows have the same number of columns.

    Args:
        table (List[List[str]]): A list of lists containing the table content.

    Returns:
        List[List[str]]: A list of lists containing the trimmed table content.
    """
