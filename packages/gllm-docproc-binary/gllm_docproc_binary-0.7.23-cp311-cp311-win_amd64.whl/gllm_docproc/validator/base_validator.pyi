from _typeshed import Incomplete
from abc import ABC
from gllm_docproc.validator.model.validator_input import ValidatorInput as ValidatorInput
from gllm_docproc.validator.model.validator_result import ValidatorResult as ValidatorResult

class BaseValidator(ABC):
    """Abstract base class for file validators.

    This class defines the interface that all file validators must implement.
    Each validator should validate a specific aspect of a file and return
    a ValidatorResult indicating success/failure and an appropriate message.
    """
    stop_on_failure: Incomplete
    applicable_extensions: Incomplete
    logger: Incomplete
    def __init__(self, stop_on_failure: bool = False, applicable_extensions: list[str] | None = None) -> None:
        """Initialize the BaseValidator.

        Args:
            stop_on_failure (bool, optional): Whether to terminate the validation process if this validator fails.
                Default is False.
            applicable_extensions (list[str] | None, optional): The list of file extensions that this validator is
                applicable to. Default is None which means all extensions are applicable.
        """
    def validate(self, file_validation_input: ValidatorInput) -> ValidatorResult:
        """Validate the file against the validator's criteria.

        Args:
            file_validation_input (ValidatorInput): The ValidatorInput object to validate.

        Returns:
            ValidatorResult: A ValidatorResult object indicating success or failure
                with an appropriate message.
        """
