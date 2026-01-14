import logging

from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import TypedDict

from requests import Response

from jsm_user_services.exception import EmailValidationError
from jsm_user_services.support.email_utils import perform_callback_function_validators
from jsm_user_services.support.email_utils import validate_format_email
from jsm_user_services.support.http_utils import get_response_body
from jsm_user_services.support.http_utils import request
from jsm_user_services.support.settings_utils import get_from_settings_or_raise_missing_config

logger = logging.getLogger(__name__)


DEFAULT_VALIDATORS_FUNCTION: List[Callable] = [validate_format_email]


class ValidationResult(TypedDict):
    is_valid: bool
    external_api_validation: bool


def perform_email_validation(
    email: str,
    use_callback_function_validator: bool = True,
    functions_to_validate_email: Optional[List[Callable]] = None,
) -> ValidationResult:
    """
    Parameters:
        `email (str)`: the e-mail that will be validated
        `use_callback_function_validator (bool)`: indicates if some validators must be considered if the `status_code`
        is different from 200 (success)
        `functions_to_validate_email (List[Callable])`: list of validators that will be considered if the `status_code`
        is different from 200 (success) and the `use_callback_function_validator` is `False`

    Returns:
        A dict containing two values:
        - `is_valid (bool)`: indicates if the email string is valid
        - `external_api_validation (bool)`: indicates if the email validation was made by Everest or locally

    Response success example:
        {
            "meta": {},
            "results": {
                "category": "valid",
                "status": "valid",
                "name": "Valid",
                "definition": "The email has a valid account associated with it.",
                "reasons": [],
                "risk": "low",
                "recommendation": "send",
                "address": "ayron41@gmail.com",
                "diagnostics": {
                    "role_address": false,
                    "disposable": false,
                    "typo": false
                }
            }
        }
    """
    functions_to_use_in_callback_validate_email = (
        functions_to_validate_email if functions_to_validate_email else DEFAULT_VALIDATORS_FUNCTION
    )
    EVEREST_LIST_INVALIDS_STATUS_RESPONSES = get_from_settings_or_raise_missing_config(
        "EVEREST_LIST_INVALIDS_STATUS_RESPONSES", "invalid"
    )
    invalid_status_list = EVEREST_LIST_INVALIDS_STATUS_RESPONSES.split(",")
    try:
        email_validation_response: Dict = get_email_validation(email)
        results: dict = email_validation_response.get("results") or {}
        status: Optional[str] = results.get("status")
        is_valid: bool = status not in invalid_status_list and status is not None
        return ValidationResult(is_valid=is_valid, external_api_validation=True)
    except Exception as err:
        logger.warning(f"Everest API Response Failed: {err}")
        if use_callback_function_validator:
            return ValidationResult(
                is_valid=perform_callback_function_validators(
                    functions_to_validate_email=functions_to_use_in_callback_validate_email, email=email
                ),
                external_api_validation=False,
            )
        raise EmailValidationError


def get_email_validation(email: str) -> Dict:
    """
    Returns the payload from Everest
    """
    EVEREST_API_KEY = get_from_settings_or_raise_missing_config("EVEREST_API_KEY", "api-key-everest")
    EVEREST_API_URL = get_from_settings_or_raise_missing_config(
        "EVEREST_API_HOST", "https://api.everest.validity.com/api/2.0/validation/addresses"
    )

    with request(status_forcelist=(429, 500, 502, 503, 504)) as r:
        url: str = f"{EVEREST_API_URL}/{email}"
        headers: Dict = {"X-API-KEY": EVEREST_API_KEY}
        response: Response = r.get(url, headers=headers)
        payload: Dict = get_response_body(response)
    logger.info(f"Everest API Response: {payload}")
    return payload
