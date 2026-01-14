"""
Module for backwards compatibility with the old drf module.

Should be removed in the future.
"""

from jsm_user_services.drf import authentications
from jsm_user_services.drf import exceptions
from jsm_user_services.drf import helpers
from jsm_user_services.drf import permissions

__all__ = ["authentications", "exceptions", "helpers", "permissions"]
