from typing import Any

def create_folder(folder_path: str) -> None:
    """Create a folder.

    This function check if the folder path exists. If the folder path does not
    exist, the function creates a folder in the specified folder path.

    Args:
        folder_path (str): The folder path to create.
    """
def create_full_path(dir_path: str, filename: str, file_extension: str) -> str:
    """Create a full path for a file.

    This function creates a full path for a file by combining the directory
    path, the filename, and the file extension.

    Args:
        dir_path (str): The directory path.
        filename (str): The filename.
        file_extension (str): The file extension.

    Returns:
        str: The full path for the file.
    """
def save_to_json(elements: list[dict[str, Any]] | dict[str, Any], folder_path: str, file_name: str) -> str:
    """Save a list of elements to a JSON file.

    This function saves a list of elements to a JSON file. The function takes
    the list of elements, the folder path, and the file name as input and saves
    the elements to a JSON file in the specified folder.

    Args:
        elements (list[dict[str, Any]] | dict[str, Any]): The list of elements to save.
        folder_path (str): The folder path to save the JSON file.
        file_name (str): The file name of the JSON file.

    Returns:
        str: The full filepath of the created JSON file.
    """
def save_to_csv(elements: list[dict[str, Any]], folder_path: str, file_name: str) -> None:
    """Save a list of elements to a CSV file.

    This function saves a list of elements to a CSV file. The function takes
    the list of elements, the folder path, and the file name as input and saves
    the elements to a CSV file in the specified folder.

    Args:
        elements (list[dict[str, Any]]): The list of elements to save.
        folder_path (str): The folder path to save the CSV file.
        file_name (str): The file name of the CSV file.

    Returns:
        None
    """
def save_file(content: str, filename: str):
    """Save the content to a file.

    Args:
        content (str): The content to save.
        filename (str): The filename to save the content to.

    Returns:
        None
    """
def read_json_file(file_path: str) -> list[dict[str, Any]] | dict[str, Any]:
    """Read a JSON file.

    This function reads a JSON file and returns the content of the JSON file.

    Args:
        file_path (str): The path of the JSON file to read.

    Returns:
        list[dict[str, Any]] | dict[str, Any]: The content of the JSON file.
    """
