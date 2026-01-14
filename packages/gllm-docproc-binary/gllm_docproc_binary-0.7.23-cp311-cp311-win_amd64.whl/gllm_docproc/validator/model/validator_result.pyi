from pydantic import BaseModel
from typing import Any

class ValidatorResult(BaseModel):
    """Represents the result of a validation operation.

    This class encapsulates the result of a validation operation, including whether
    the validation passed or failed and any associated message.

    Attributes:
        is_valid (bool): Whether the validation passed or failed.
        source_validator (str): Validator class name that produced this result.
        message (str): The message associated with the validation result.
        params (dict[str, Any]): The parameters associated with the validation result.
    """
    is_valid: bool
    source_validator: str
    message: str
    params: dict[str, Any]
