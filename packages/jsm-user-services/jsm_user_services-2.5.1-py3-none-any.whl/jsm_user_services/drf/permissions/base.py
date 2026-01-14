import logging

from requests.exceptions import HTTPError
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from jsm_user_services import settings
from jsm_user_services.services.user import get_user_data_from_server

logger = logging.getLogger(__name__)


class JSMUserBasePermission(permissions.BasePermission):
    """
    Base class for JSM user permissions. Implements methods for validating requests against
    the user micro service so that any type of permission can be carried out (role, status, etc).
    """

    APPEND_USER_DATA = settings.JSM_USER_SERVICES_DRF_APPEND_USER_DATA
    USER_DATA_ATTR_NAME = settings.JSM_USER_SERVICES_DRF_REQUEST_USER_DATA_ATTR_NAME
    USER_SERVICE_NOT_AUTHORIZED_CODES = (401, 403, 404)

    _decoded_jwt_token: dict | None = None
    _decoded_jwt_token_keys: set[str] | None = None

    _protected: bool = False
    _forbidden: bool = False
    _protected_keys: set[str] | None = None

    @classmethod
    def _retrieve_user_data(cls, request: Request) -> dict:
        try:
            user_data = getattr(request, cls.USER_DATA_ATTR_NAME)
        except AttributeError:
            user_data = get_user_data_from_server()

        return user_data

    @classmethod
    def _validate_request_against_user_service(cls, request: Request, append_user_data_to_request: bool = True) -> dict:
        """
        Gets valid user_data from the User micro service.
        """
        if not settings.JSM_USER_SERVICE_REQUEST_USER_DATA:
            return {}

        try:
            user_data: dict = cls._retrieve_user_data(request)

            if append_user_data_to_request:
                setattr(request, cls.USER_DATA_ATTR_NAME, user_data)

        except HTTPError as e:
            if e.response.status_code in cls.USER_SERVICE_NOT_AUTHORIZED_CODES:
                return {}

            raise

        return user_data

    def decode_jwt_token(self, request: Request) -> tuple[dict, set[str]]:
        if self._decoded_jwt_token and self._decoded_jwt_token_keys:
            return self._decoded_jwt_token, self._decoded_jwt_token_keys

        decoded_token = getattr(request, "jsm_token_payload", None)
        logger.debug("Decoded token: %s", decoded_token)

        if not decoded_token:
            raise ValueError("Decoded token is not present in the request")

        self._decoded_jwt_token = decoded_token
        self._decoded_jwt_token_keys = {key.lower() for key in decoded_token.keys()}
        return decoded_token, self._decoded_jwt_token_keys

    def _protect(self, request: Request) -> bool:
        setattr(request, "is_protected", self._protected)
        setattr(request, "protected_keys", self._protected_keys or set())
        setattr(request, "should_return_forbidden", self._forbidden)

        _, decoded_token_keys = self.decode_jwt_token(request)
        if self._forbidden and decoded_token_keys and "fid" in decoded_token_keys:
            return False

        return True

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Abstract method that must be implemented by children classes.
        """
        is_valid = True

        if self._protected:
            is_valid = self._protect(request)

        return is_valid


def protected(
    cls: type["JSMUserBasePermission"], keys: set[str] | None = None, should_return_forbidden: bool = False
) -> type["JSMUserBasePermission"]:
    """
    Decorator to mark a permission as protected.
    """
    cls._protected = True
    cls._forbidden = should_return_forbidden
    cls._protected_keys = keys or set()
    return cls
