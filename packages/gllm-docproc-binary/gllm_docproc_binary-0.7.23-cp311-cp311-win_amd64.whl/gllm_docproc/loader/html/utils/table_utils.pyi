from _typeshed import Incomplete
from gllm_docproc.loader.html.utils.string_utils import StringUtils as StringUtils
from gllm_docproc.utils.html_constants import TableConstants as TableConstants
from typing import Any

class TableUtils:
    """A utility class providing methods for extracting data from HTML tables."""
    colcount: int
    table_selector: Incomplete
    rowspans: Incomplete
    def __init__(self, table_selector) -> None:
        """Initialize TableUtils with the given table selector.

        Args:
            table_selector: Selector for the HTML table.
        """
    def get_table(self) -> dict[str, Any]:
        """Extract data from the HTML table and return it as a dictionary."""
    def extract_table(self):
        """Extract data from the HTML table and return it as a list of lists representing the table structure."""
    def extract_table_row_type(self):
        """Extract metadata from the HTML table and return it as a list of strings representing the row types."""
    def update_col_count(self, row_cells, prev_rowspans) -> None:
        """Update the number of columns in the table.

        Args:
            row_cells: List of HTML cells in a row.
            prev_rowspans: List of previous rowspans.
        """
    def get_row_type(self, row):
        """Get the type of the row.

        Args:
            row: HTML row.
        """
    def extract_max_char_count(self, table):
        """Extract maximum character count.

        Extract metadata from the HTML table and return it as a list of integers representing
        the maximum number of characters in each column.

        Args:
            table: List of lists representing the table structure.

        Returns:
            list: A list of integers representing the maximum number of characters in each column.
        """
    @staticmethod
    def convert_to_texts(table) -> list[str]:
        """Convert to texts.

        This method processes table content by iterating over its metadata, handling each row based
        on its type, and appending the result to the table data.

        Args:
            table: table which will be converted to text

        Returns:
            list: A list of dictionaries containing the extracted table data.
        """
    @staticmethod
    def print_row(row, col_size=None):
        """Formats a table row.

        Args:
            row (list): The row to be formatted.
            col_size (list | None): List of max characters size in each column

        Returns:
            str: The formatted row.
        """
    @staticmethod
    def print_table_separator(row):
        """Formats a table separator.

        Returns:
            str: The formatted table separator.
        """
