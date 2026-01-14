from _typeshed import Incomplete
from gllm_docproc.validator.base_validator import BaseValidator as BaseValidator
from gllm_docproc.validator.model.validator_input import ValidatorInput as ValidatorInput
from gllm_docproc.validator.model.validator_result import ValidatorResult as ValidatorResult

class FileSizeValidator(BaseValidator):
    """Validator for checking if file size does not exceed a maximum limit."""
    max_file_size: Incomplete
    def __init__(self, max_file_size: int = 10485760, stop_on_failure: bool = True, applicable_extensions: list[str] | None = None) -> None:
        """Initialize the FileSizeValidator.

        Args:
            max_file_size (int, optional): The maximum allowed size for the file in bytes.
                Default is 10,485,760 bytes (10MB). It should be greater than 0.
            stop_on_failure (bool, optional): Whether to stop the validation process if this
                validator fails. Default is True.
            applicable_extensions (list[str] | None, optional): The list of file extensions
                that this validator is applicable to. Default is None which means
                all extensions are applicable.
        """
