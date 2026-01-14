from _typeshed import Incomplete
from gllm_docproc.loader.csv.pandas_loader import CSV_VARIANTS as CSV_VARIANTS
from gllm_docproc.validator.base_validator import BaseValidator as BaseValidator
from gllm_docproc.validator.model.validator_input import ValidatorInput as ValidatorInput
from gllm_docproc.validator.model.validator_result import ValidatorResult as ValidatorResult

class CharacterCountValidator(BaseValidator):
    """Validator for checking if the total character length of file content does not exceed a maximum limit.

    Character length counting is currently supported for:
        - CSV files (csv, tsv, psv, ssv)
        - TXT files
    """
    CHUNK_SIZE_BYTES: Incomplete
    max_character_length: Incomplete
    def __init__(self, max_character_length: int = 500000, stop_on_failure: bool = False, applicable_extensions: list[str] | None = None) -> None:
        """Initialize the CharacterCountValidator.

        Args:
            max_character_length (int, optional): The maximum allowed character length for the file.
                Default is 500,000 characters. It should be greater than 0.
            stop_on_failure (bool, optional): Whether to stop the validation process if this
                validator fails. Default is False.
            applicable_extensions (list[str] | None, optional): The list of file extensions that this validator
                is applicable to. Default is None which means all extensions are applicable.
        """
