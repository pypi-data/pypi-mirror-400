from gllm_docproc.validator.base_validator import BaseValidator as BaseValidator
from gllm_docproc.validator.model.validator_input import ValidatorInput as ValidatorInput
from gllm_docproc.validator.model.validator_result import ValidatorResult as ValidatorResult

class PipelineValidator:
    """A pipeline for validating files against multiple validation rules.

    This class provides a flexible way to validate files by chaining multiple `BaseValidator`
    instances. Each validator is applied sequentially, and validation behavior depends on
    the `stop_on_failure` setting of each validator.

    Attributes:
        validators (list[BaseValidator]): A list of `BaseValidator` instances to apply for file validation.
    """
    validators: list[BaseValidator]
    def __init__(self) -> None:
        """Initialize the PipelineValidator object."""
    def add_validator(self, validator: BaseValidator) -> PipelineValidator:
        """Add a validator to the validation pipeline.

        Args:
            validator (BaseValidator): The validator to add to the pipeline.

        Returns:
            PipelineValidator: The validation pipeline object for method chaining.
        """
    def validate(self, file_validation_input: ValidatorInput) -> list[ValidatorResult]:
        """Validate the file against all configured validation rules.

        Validation stops early if a validator fails and its `stop_on_failure`
        setting is True; in that case, the returned list will only include results
        up to and including the failing validator.

        Args:
            file_validation_input (ValidatorInput): The file validation input object to validate.

        Returns:
            list[ValidatorResult]: A list of ValidatorResult objects for each validator run,
                which may be truncated if a validator with `stop_on_failure=True` fails.
        """
