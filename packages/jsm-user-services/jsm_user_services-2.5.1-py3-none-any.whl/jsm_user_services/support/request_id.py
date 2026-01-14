from importlib import import_module
from typing import Callable

from jsm_user_services.exception import RequestIDModuleNotFound
from jsm_user_services.support.import_utils import import_module_otherwise_none


def parse_meta_header_to_request_header(value: str) -> str:
    return value.replace("HTTP_", "").replace("_", "-")


def get_request_id_header_name() -> str:
    """
    Helper function to get request_id header name to included in request to another application
    REQUEST_ID_CONFIG dict configuration exists in the projects with similarity structure below
    REQUEST_ID_CONFIG = {
        "REQUEST_ID_HEADER": "HTTP_X_REQUEST_ID",
        "GENERATE_REQUEST_ID_IF_NOT_FOUND": True,
        "RESPONSE_HEADER_REQUEST_ID": "HTTP_X_REQUEST_ID",
    }
    """
    settings = import_module("jsm_user_services.settings")
    default_request_id_header_name = getattr(settings, "REQUEST_ID_HEADER_NAME", "HTTP_X_REQUEST_ID")
    default_request_id_config = {
        "GENERATE_REQUEST_ID_IF_NOT_FOUND": True,
        "REQUEST_ID_HEADER": default_request_id_header_name,
        "RESPONSE_HEADER_REQUEST_ID": default_request_id_header_name,
    }
    request_id_config = getattr(settings, "REQUEST_ID_CONFIG", default_request_id_config)
    if request_id_config and isinstance(request_id_config, dict) and request_id_config.get("REQUEST_ID_HEADER"):
        return parse_meta_header_to_request_header(
            request_id_config.get("REQUEST_ID_HEADER", default_request_id_header_name)
        )
    return parse_meta_header_to_request_header(default_request_id_header_name)


def get_current_request_id_callable() -> Callable:
    django_request_id_module = import_module_otherwise_none("request_id_django_log.request_id")

    if django_request_id_module is not None:
        return django_request_id_module.current_request_id

    raise RequestIDModuleNotFound


current_request_id = get_current_request_id_callable()
request_id_header_name = get_request_id_header_name()
