from .html_nested_element_handler import get_element as get_element
from gllm_docproc.loader.html.exception import HtmlLoadException as HtmlLoadException
from gllm_docproc.loader.html.nested.dictionary_utils import DictionaryUtils as DictionaryUtils
from gllm_docproc.loader.html.utils.removed_components import RemovedComponents as RemovedComponents
from gllm_docproc.loader.html.utils.string_utils import StringUtils as StringUtils
from gllm_docproc.loader.html.utils.table_utils import TableUtils as TableUtils
from gllm_docproc.utils.html_constants import ContentDataKeys as ContentDataKeys, HTMLTags as HTMLTags

def get_element_content(content_selector, removed_components: RemovedComponents) -> list[dict]:
    '''Traverses each element to get the content.

    This function extract html body recursively

    Input example:

    .. code-block:: html

        <html>
        <head>
        <title>Title</title>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to My Website</h1>
                <div>
                    Hello World
                </div>
            </div>
            <p>This is another paragraph.</p>
        </body>
        </html>

    Output:

    .. code-block:: groovy

        [
            {
                \'tag\': \'body\',
                \'class\': None,
                \'content\': [
                    {
                        \'tag\': \'div\',
                        \'class\': \'container\',
                        \'content\': [
                            {
                                \'tag\': \'h1\',
                                \'class\': None, \'content\': [
                                    {
                                        \'tag\': \'text\',
                                        \'content\': \'Welcome to My Website\'
                                    }
                                ]
                            },
                            {
                                \'tag\': \'div\',
                                \'class\': None,
                                \'content\': [
                                    {\'tag\': \'text\', \'content\': \'Hello World\'}
                                ]
                            }
                        ]
                    },
                    {
                        \'tag\': \'p\',
                        \'class\': None,
                        \'content\': [
                            {\'tag\': \'text\', \'content\': \'This is another paragraph.\'}
                        ]
                    }
                ]
            }
        ]

    Args:
        content_selector: The content to be traversed.
        removed_components: Removed class or tags.

    Returns:
        The List of extracted contents.
    '''
def is_base_element(content_selector, removed_components: RemovedComponents) -> bool:
    """Check if the given content selector represents a base element.

    See html_flat_base_handler.py for more information.

    Args:
        content_selector: The content selector to check.
        removed_components (RemovedComponents): An instance of RemovedComponents class.

    Returns:
        bool: True if the content_selector represents a base element; False otherwise.
    """
def handle_base_element(content_selector, removed_components: RemovedComponents) -> list[dict]:
    """Handle the processing of a base HTML element.

    Args:
        content_selector: The content selector representing the HTML element.
        removed_components (RemovedComponents): An object containing information about components to be removed.

    Returns:
        List of dict : A List of dictionaries containing information about the HTML element, or None
                      if the element should be skipped.
                      - tag: HTML tag name.
                      - class: CSS class of the element (if available).
                      Additional keys may be added based on the specific element handler.
    """
def get_handler(tag: str):
    """Get the element information from the specified content selector.

    Args:
        tag (str): The HTML tag to get the handler for.

    Returns:
        dict: A dictionary containing information about the HTML element.
              - tag: HTML tag name.
              - class: CSS class of the element (if available).
              Additional keys may be added based on the specific element handler
    """
def create_text_dict(message):
    """Creates a dictionary with 'text' tag and specified content.

    Args:
        message: The content to be added to the dictionary.

    Returns:
        A dictionary with 'text' tag and specified content.
    """
