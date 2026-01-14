from gllm_docproc.model.element import Element as Element

class NestedElement(Element):
    """A specialized class extending Element to represent nested elements.

    This class includes additional functionality specific to nested elements, such as generating
    a unique element_id and providing methods to convert the instance to a dictionary or Element.

    Attributes:
        element_id (int): A unique identifier for the nested element.

    Methods:
        to_dict(): Convert the NestedElement instance to a dictionary.
        to_element(): Convert the NestedElement instance to an Element.
    """
    element_id: int
    def to_dict(self):
        """Convert the NestedElement instance to a dictionary.

        Returns:
            dict: A dictionary representation of the NestedElement instance.
        """
    def to_element(self) -> Element:
        """Convert the NestedElement instance to an Element.

        This method creates an Element instance from the current NestedElement. It deep copies the metadata,
        assigns the element_id, and constructs an Element with the associated text, metadata, and structure.

        Returns:
            Element: The Element instance created from the NestedElement.
        """
