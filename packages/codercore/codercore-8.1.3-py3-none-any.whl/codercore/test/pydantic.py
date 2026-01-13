import copy
from typing import Any

from pydantic import ValidationError


def check_required_field_errors(
    required_field_names: list[str], errors: list[dict]
) -> bool:
    errors = copy.deepcopy(errors)
    for required_field_name in required_field_names:
        i = _get_index_for_field_name(required_field_name, errors)
        if i == -1:
            return False
        del errors[i]
    return True


def _get_index_for_field_name(field_name: str, errors: list[dict]) -> int:
    for i, error in enumerate(errors):
        if error["loc"][-1] == field_name and error["type"] == "value_error.missing":
            return i
    return -1


def check_validation_value_error(
    error: ValidationError,
    location: tuple[str, ...],
    message: str,
    input_: Any,
) -> bool:
    errors = error.errors()
    if len(errors) != 1:
        return False

    error_data = _remove_redundant_validation_error_data(errors[0])

    return error_data == {
        "loc": location,
        "msg": f"Value error, {message}",
        "input": input_,
        "type": "value_error",
    }


def _remove_redundant_validation_error_data(error_data: dict) -> dict:
    error_data = copy.copy(error_data)
    del error_data["url"]
    del error_data["ctx"]
    return error_data
