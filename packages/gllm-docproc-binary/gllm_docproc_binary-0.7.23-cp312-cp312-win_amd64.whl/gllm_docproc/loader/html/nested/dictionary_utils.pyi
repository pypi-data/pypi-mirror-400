class DictionaryUtils:
    """A utility class providing methods to manipulate dictionaries."""
    @staticmethod
    def add_or_skip_value(dictionary, key, value):
        """Adds a value to a dictionary if the value is not None for a given key.

        Args:
            dictionary (dict): The dictionary to be modified.
            key (hashable): The key where the value needs to be added.
            value (any): The value to be added.

        Returns:
            dict: The modified dictionary.
        """
    @staticmethod
    def append_value(dictionary, key, value):
        """Appends a value to a list under a specific key in a dictionary.

        If the key already exists in the dictionary, the value is appended to the list under that key.
        If the key does not exist, a new list is created with the value as its first element.

        Args:
            dictionary (dict): The dictionary to be modified.
            key (hashable): The key under which the value needs to be added.
            value (any): The value to be appended to the list under the key.

        Returns:
            dict: The modified dictionary with the value appended to the list under the key.
        """
    @staticmethod
    def put_key_to_bottom(dictionary, key):
        """Rearange key in dictionary.

        Args:
            dictionary (dict): The dictionary to be modified.
            key (hashable): The key.

        Returns:
            dict: The modified dictionary.
        """
