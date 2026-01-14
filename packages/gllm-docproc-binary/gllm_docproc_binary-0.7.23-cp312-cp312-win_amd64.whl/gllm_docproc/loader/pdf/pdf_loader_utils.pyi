from gllm_docproc.model.element import Element as Element, UNCATEGORIZED_TEXT as UNCATEGORIZED_TEXT
from typing import Any

def merge_loaded_elements_by_coordinates(loaded_elements: list[Element], existing_loaded_elements: list[Element], **kwargs: Any) -> list[Element]:
    """Merge the loaded elements by coordinates.

    This function merges elements from 'loaded_elements' into 'existing_loaded_elements' based on
    coordinates. The 'loaded_elements' inside the 'existing_loaded_elements' (eg. table) will be
    duplicated information and will not be included in the merged list.

    Args:
        loaded_elements (List[Element]): A list of Elements containing loaded element content.
        existing_loaded_elements (List[Element]): A list of existing Elements.
        kwargs (Any): Additional keyword arguments for merging the loaded elements.

    Kwargs:
        is_object_inside_box_threshold (float, optional): The threshold of the intersection area to the area
            of the object. Defaults to 1.
        merge_element_with_duplicates (Callable[[Element, List[Element]], Element], optional): The function
            to merge the new element with the duplicate elements. Defaults to _merge_element_with_duplicates.

    Returns:
        list[Element]: A list of Element containing merged loaded element content.
    """
def bbox_to_coordinates(bbox: list[float]) -> list[int]:
    """Convert the bounding box to coordinates.

    This method converts the bounding box to coordinates.

    Args:
        bbox (list[float]): The bounding box.

    Returns:
        list[int]: The coordinates.
    """
def is_object_inside_box(object_coordinates: list[int], box_coordinates: list[int], threshold: float = 1) -> bool:
    """Validate is object coordinates position inside the box.

    Args:
        object_coordinates (list[int]): The coordinates position of the object.
        box_coordinates (list[int]): The coordinates position of the box.
        threshold (float): The threshold of the intersection area to the area of the object.

    Returns:
        bool: True if the object coordinates position inside the box.
    """
def calculate_object_intersection_over_box_area(object_coordinates: list[int], box_coordinates: list[int]) -> float:
    """Calculate the ratio of the intersection area of an object to the area of a bounding box.

    This function computes the area of intersection between the given object coordinates and box coordinates,
    and then calculates the ratio of this intersection area to the area of the object.

    Args:
        object_coordinates (list[int]): The coordinates of the object in the format [left, right, bottom, top].
        box_coordinates (list[int]): The coordinates of the bounding box in the format [left, right, bottom, top].

    Returns:
        float: The ratio of the intersection area to the area of the object. Returns 0 if there is no intersection.
    """
