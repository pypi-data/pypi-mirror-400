class RemovedComponents:
    """Class representing removed components from a document.

    This class defines three methods for retrieving partial class, full class, and HTML tags
    associated with removed components.
    """
    def get_partial_class(self) -> list[str]:
        """Get partial class.

        Method to get the partial class of the removed component. Partial class consists of
        classes that will be filtered.

        Returns:
            str: The partial class name associated with the removed component.
        """
    def get_full_class(self) -> list[str]:
        """Get full class.

        Method to get the full class of the removed component. Full class consists of
        exact match of classes that will be filtered.

        Returns:
            str: The full class name associated with the removed component.
        """
    def get_html_tags(self) -> list[str]:
        """Method to get the HTML tags associated with the removed component.

        Returns:
            list: A list of HTML tags associated with the removed component.
        """
    @staticmethod
    def is_removed_component(tag: str | None, class_: str | None, removed_components: RemovedComponents | None) -> bool:
        """Checks if a component should be removed based on its tag and class.

        Args:
            tag (str): The tag of the component.
            class_ (str): The class of the component.
            removed_components (RemovedComponents): The components to be removed, including HTML tags and classes.

        Returns:
            True if the component should be removed, False otherwise.
        """
    @staticmethod
    def check_list_in_substring(message: str, check_list: list[str]) -> bool:
        """Checks if any substring from the check_list exists in the message string.

        Args:
            message (str): The string to search for substrings.
            check_list (list): A list of substrings to be checked.

        Returns:
        - bool: True if any substring from check_list is found in message, otherwise False.
        """
