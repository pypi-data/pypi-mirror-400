from django.conf import settings

from jsm_user_services.exception import MissingRequiredConfiguration


def get_settings_or_raise_missing_config(
    settings_key: str, default: str | None = None, cast: type = str, required: bool = True
):
    value = getattr(settings, settings_key, default)

    if value is None and required:
        raise MissingRequiredConfiguration(f"The variable {settings_key} is missing")
    elif value is None:
        return default

    return cast(value)


# User Service related settings
USER_API_HOST = get_settings_or_raise_missing_config("USER_API_HOST")
USER_API_TOKEN = get_settings_or_raise_missing_config("USER_API_TOKEN")
USER_API_PROFILE_ENDPOINT = get_settings_or_raise_missing_config("USER_API_PROFILE_ENDPOINT", "/v1/users/me/")
USER_API_SELLER_PROFILE_ENDPOINT = get_settings_or_raise_missing_config(
    "USER_API_SELLER_PROFILE_ENDPOINT", "/v1/me/sellers/"
)
JSM_USER_SERVICE_REQUEST_USER_DATA = get_settings_or_raise_missing_config(
    "JSM_USER_SERVICE_REQUEST_USER_DATA", "True", cast=bool
)
JSM_USER_SERVICE_HTTP_TIMEOUT = get_settings_or_raise_missing_config("JSM_USER_SERVICE_HTTP_TIMEOUT", "30", cast=float)
JSM_USER_SERVICES_DRF_APPEND_USER_DATA = get_settings_or_raise_missing_config(
    "JSM_USER_SERVICES_DRF_APPEND_USER_DATA", "True", cast=bool
)
JSM_USER_SERVICES_DRF_REQUEST_USER_DATA_ATTR_NAME = get_settings_or_raise_missing_config(
    "JSM_USER_SERVICES_DRF_REQUEST_USER_DATA_ATTR_NAME", "jsm_user_data"
)
REQUEST_ID_CONFIG = get_settings_or_raise_missing_config("REQUEST_ID_CONFIG", required=False, cast=dict)

# JWT related settings
JSM_JWT_ALGORITHM = get_settings_or_raise_missing_config("JSM_JWT_ALGORITHM", "HS256")
JSM_JWT_DECODE = get_settings_or_raise_missing_config("JSM_JWT_DECODE", "True", cast=bool)
JSM_JWT_SHOULD_VERIFY_SIGNATURE = get_settings_or_raise_missing_config(
    "JSM_JWT_SHOULD_VERIFY_SIGNATURE", "False", cast=bool
)
JSM_JWT_SECRET_KEY = get_settings_or_raise_missing_config("JSM_JWT_SECRET_KEY", required=False)
JSM_JWT_AUDIENCE = get_settings_or_raise_missing_config("JSM_JWT_AUDIENCE", default="audience")

# Google Recaptcha related settings
GOOGLE_RECAPTCHA_URL = get_settings_or_raise_missing_config("GOOGLE_RECAPTCHA_URL", required=False)
GOOGLE_RECAPTCHA_SECRET_KEY = get_settings_or_raise_missing_config("GOOGLE_RECAPTCHA_SECRET_KEY", required=False)
GOOGLE_RECAPTCHA_SCORE_THRESHOLD = get_settings_or_raise_missing_config(
    "GOOGLE_RECAPTCHA_SCORE_THRESHOLD", required=False
)
GOOGLE_RECAPTCHA_BYPASS_IP_HEADER_NAME = get_settings_or_raise_missing_config(
    "GOOGLE_RECAPTCHA_BYPASS_IP_HEADER_NAME", required=False
)

# Everest related settings
EVEREST_API_KEY = get_settings_or_raise_missing_config("EVEREST_API_KEY", required=False)
EVEREST_API_HOST = get_settings_or_raise_missing_config("EVEREST_API_HOST", required=False)
EVEREST_LIST_INVALIDS_STATUS_RESPONSES = get_settings_or_raise_missing_config(
    "EVEREST_LIST_INVALIDS_STATUS_RESPONSES", required=False
)
