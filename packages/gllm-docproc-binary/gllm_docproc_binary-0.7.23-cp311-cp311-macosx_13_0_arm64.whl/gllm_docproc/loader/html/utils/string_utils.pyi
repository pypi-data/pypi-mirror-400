class StringUtils:
    """A utility class providing methods for text cleaning."""
    @staticmethod
    def clean_text(text: str | None) -> str:
        """Clean the input text by removing extra whitespace, newlines, and tabs.

        Args:
            text (str): The text to be cleaned.

        Returns:
            str: The cleaned text.
        """
    @staticmethod
    def remove_extension(file_name: str) -> str:
        """Removes the file extension from a given file name.

        Args:
            file_name (str): The name of the file from which the extension will be removed.

        Returns:
            str: File name without the extension.
        """
    @staticmethod
    def append_character(text: str, new_char: str) -> str:
        """Appends a character to the end of a string, handling newline endings.

        Args:
            text (str): The input text string to which the character will be appended.
            new_char (str): The character to append to the text.

        Returns:
            str: The modified string with the appended character.
        """
