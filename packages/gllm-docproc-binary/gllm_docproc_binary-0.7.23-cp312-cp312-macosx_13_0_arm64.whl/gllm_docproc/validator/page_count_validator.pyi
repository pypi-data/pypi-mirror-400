from _typeshed import Incomplete
from gllm_docproc.validator.base_validator import BaseValidator as BaseValidator
from gllm_docproc.validator.model.validator_input import ValidatorInput as ValidatorInput
from gllm_docproc.validator.model.validator_result import ValidatorResult as ValidatorResult

class PageCountValidator(BaseValidator):
    """Validator for checking if the number of pages in a file does not exceed a maximum limit.

    Page counting is currently supported for PDF files only.
    """
    max_pages: Incomplete
    def __init__(self, max_pages: int = 100, stop_on_failure: bool = False, applicable_extensions: list[str] | None = None) -> None:
        """Initialize the PageCountValidator.

        Args:
            max_pages (int, optional): The maximum allowed number of pages. A non-negative
                value enforces a limit. Default is 100 pages. It should be greater than 0.
            stop_on_failure (bool, optional): Whether to stop the validation process if this
                validator fails. Default is False.
            applicable_extensions (list[str] | None, optional): The list of file extensions
                that this validator is applicable to. Default is None which means
                all extensions are applicable.
        """
