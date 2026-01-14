from typing import Optional

from jsm_user_services import settings
from jsm_user_services.exception import MissingRequiredConfiguration


def get_from_settings_or_raise_missing_config(name: str, default: Optional[str] = None) -> str:
    """
    Tries to retrieve the value from attribute in settings. If it was not possible to retrieve the value, raises.
    """

    # getattr can return None when the attribute exists and the value is None
    value = getattr(settings, name, default) or default
    if value is None:
        raise MissingRequiredConfiguration(f"The variable {name} is missing")

    return value
