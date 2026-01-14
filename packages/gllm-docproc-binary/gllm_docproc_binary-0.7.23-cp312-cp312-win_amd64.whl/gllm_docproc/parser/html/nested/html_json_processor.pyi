from _typeshed import Incomplete
from gllm_docproc.model.element import PARAGRAPH as PARAGRAPH, TABLE as TABLE, TITLE as TITLE
from gllm_docproc.parser.html.nested.nested_element import NestedElement as NestedElement
from gllm_docproc.utils.html_constants import ContentDataKeys as ContentDataKeys, ErrorMessage as ErrorMessage, FORMATTING_TAGS as FORMATTING_TAGS, HTMLTags as HTMLTags, ItemDataKeys as ItemDataKeys, MetaDataKeys as MetaDataKeys, SPACING as SPACING, Structure as Structure, TableConstants as TableConstants

class HTMLJsonProcessor:
    """Processor for processing items scraped by the spider.

    This pipeline processes the raw data scraped by the spider, formats it, and stores it in a JSON format.
    It also handles errors during the processing and logging of the data.

    Attributes:
        logger: An instance of a logger, used for logging runtime information.
        element_id: A counter for the elements processed by the pipeSline.
        processor_result: A dictionary that holds the processed data.
    """
    logger: Incomplete
    element_id: int
    processor_result: Incomplete
    def __init__(self) -> None:
        """Initialize the HTMLJsonProcessor."""
    def process_item(self, item: list[dict]):
        """Processes each item passed by the spider.

        The method formats the raw data and stores it in the processor_result dictionary.

        Args:
            item (list): The raw data scraped by the spider.

        Returns:
            list: The processed item.
        """
    def add_title_element(self, item) -> None:
        """Adds the title element to the processor_result dictionary.

        Args:
            item (dict): The raw data scraped by the spider.
        """
    def extract_data(self, current: dict, data: NestedElement):
        """Extracts data from the raw data.

        This method traverses the raw data and extracts the necessary information.

        Args:
            current (dict): The current node in the raw data.
            data (NestedElement): The dictionary where the extracted data is stored.
        """
    def handle_table_data(self, current, data: NestedElement):
        """Handles table content.

        Args:
            current (dict): The current node in the raw data. It should contain the table content and metadata.
            data (dict): The dictionary where the extracted data is stored.
        """
    def handle_media_data(self, current, data: NestedElement):
        """Handles media content.

        Args:
            current (dict): The current node in the raw data.
            data (dict): The dictionary where the extracted data is stored.
        """
    def handle_string_content(self, current, data: NestedElement):
        """Handles string content.

        Args:
            current (dict): The current node in the raw data.
            data (dict): The dictionary where the extracted data is stored.
        """
    def handle_other_cases(self, current, data: NestedElement):
        """Handles other cases.

        Args:
            current (dict): The current node in the raw data.
            data (dict): The dictionary where the extracted data is stored.
        """
    def handle_current_tag(self, current, data: NestedElement) -> tuple[NestedElement, dict]:
        """Handles the current tag. This method checks the current tag and updates the data accordingly.

        Args:
            current (dict): The current node in the raw data.
            data (dict): The dictionary where the extracted data is stored.

        Returns:
            NestedElement: The updated NestedElement object.
            dict: A dictionary containing additional arguments.
        """
    def handle_content(self, current, data: NestedElement, args: dict):
        """Handles content. This method iterates over the content and extracts the necessary information.

        Args:
            current (dict): The current node in the raw data.
            data (NestedElement): The dictionary where the extracted data is stored.
            args (dict): The dictionary containing the arguments for the method.
        """
    def add_result(self, data: NestedElement):
        """Adds the processed data to the processor_result dictionary.

        Args:
            data (dict): The processed data.
        """
    def add_link(self, data: NestedElement) -> NestedElement:
        """Adds a link to the processed data content.

        Args:
            data (dict): The processed data.

        Returns:
            dict: The processed data.
        """
    def add_index(self, data: NestedElement) -> NestedElement:
        """Adds a index to the processed data content.

        Args:
            data (dict): The processed data.

        Returns:
            dict: The processed data.
        """
    def handle_media(self, current, data: NestedElement) -> NestedElement:
        """Handles media content.

        Args:
            current (dict): The current node in the raw data.
            data (dict): The dictionary where the extracted data is stored.

        Returns:
            dict: The processed data.
        """
    def handle_table(self, current, data: NestedElement) -> list:
        """Handle Table.

        This method processes table content by iterating over its metadata, handling each row based on its type,
        and appending the result to the table data.

        Args:
            current (dict): The current node in the raw data. It should contain the table content and metadata.
            data (dict): The dictionary where the extracted data is stored. This method adds a 'structure' key with the
                         value 'table', and appends the extracted table data to this dictionary.

        Returns:
            list: A list of dictionaries containing the extracted table data.
        """
    def print_row(self, row, col_size=None):
        """Formats a table row.

        Args:
            row (list): The row to be formatted.
            col_size (list | None, optional): The size of the columns. Defaults to None.

        Returns:
            str: The formatted row.
        """
    def print_table_separator(self, row):
        """Formats a table separator.

        Returns:
            str: The formatted table separator.
        """
