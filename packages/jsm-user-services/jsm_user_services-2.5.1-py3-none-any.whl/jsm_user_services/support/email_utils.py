import re

from typing import Callable
from typing import List


def validate_format_email(email: str) -> bool:
    """
    Check if the given string has a valid format e-mail
    """
    regex = r"\b^[A-Za-z0-9](([_\.\-]?[a-zA-Z0-9\_]+)*)@([A-Za-z0-9]+)(([\.\-]?[a-zA-Z0-9]+)*)\.([A-Za-z]{2,})$\b"
    return bool(re.match(regex, email))


def perform_callback_function_validators(functions_to_validate_email: List[Callable], email: str) -> bool:
    """
    Returns if the e-mail is valid by `functions_to_validate_email`
        Parameters:
            `functions_to_validate_email (List[Callable])`: a list of functions to validate the e-mail
            `email (str)`: the e-mail that will be validated
    """
    for check in functions_to_validate_email:
        checkResult = check(email)
        if not checkResult:
            return False
    return True
