import logging

from typing import Generic
from typing import TypeVar
from typing import cast
from typing import override

import jwt

from django.contrib.auth.models import AnonymousUser
from requests import HTTPError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import status

from jsm_user_services import settings
from jsm_user_services.drf.exceptions import AuthenticationSkipped
from jsm_user_services.drf.exceptions import ExpiredToken
from jsm_user_services.drf.exceptions import InvalidToken
from jsm_user_services.drf.exceptions import NotAuthenticated
from jsm_user_services.drf.models import JsmUser
from jsm_user_services.drf.models import LoUser
from jsm_user_services.drf.models import LvSellerUser
from jsm_user_services.drf.models import LvUser
from jsm_user_services.services.user import current_jwt_token
from jsm_user_services.services.user import get_seller_user_data_from_server
from jsm_user_services.services.user import get_user_data_from_server
from jsm_user_services.support.auth_jwt import decode_jwt_token
from jsm_user_services.typings import Auth0TokenPayload
from jsm_user_services.typings import JsmRequest
from jsm_user_services.typings import LoTokenPayload
from jsm_user_services.typings import LoUserData
from jsm_user_services.typings import LvSellerData
from jsm_user_services.typings import LvTokenPayload
from jsm_user_services.typings import LvUserData

logger = logging.getLogger(__name__)

UserType = TypeVar("UserType", dict, AnonymousUser, JsmUser, LoUser, LvUser, LvSellerUser)
JwtPayloadType = TypeVar("JwtPayloadType", dict, Auth0TokenPayload, LoTokenPayload, LvTokenPayload)


class BaseJsmAuthentication(BaseAuthentication, Generic[JwtPayloadType, UserType]):
    """
    Base class for JWT authentication classes.

    Provides a method to retrieve user data from the request or from the user microservice.
    """

    user_claim: str = "sub"
    inject_user_data_to_request = settings.JSM_USER_SERVICES_DRF_APPEND_USER_DATA

    user_data: UserType
    user_id: str = "id"
    token: str = ""

    def __init__(self, *args, **kwargs) -> None:
        self.user_data = cast(UserType, {})

    def get_user_data_from_server(self) -> UserType:
        return cast(UserType, get_user_data_from_server())

    def get_user_data(self, request: JsmRequest) -> UserType:
        if self.user_data:
            return self.user_data

        try:
            user_data = self.get_user_data_from_server()
        except HTTPError as http_error:
            if http_error.response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
                logger.debug("User not authorized in user service")
                raise AuthenticationFailed("User not authorized in user service") from http_error

            if http_error.response.status_code == status.HTTP_404_NOT_FOUND:
                logger.debug("User not found in user service")
                raise AuthenticationFailed("User not found") from http_error

            logger.exception("Failed to retrieve user data from server")
            raise AuthenticationFailed("Could not retrieve user data from server") from http_error

        if not isinstance(user_data, (dict, list)):
            logger.debug("User data is not a dictionary or list")
            raise AuthenticationFailed("User data is not a dictionary or list")

        if isinstance(user_data, dict):
            user_payload = user_data.get("data", user_data)
        else:
            user_payload = user_data[0]

        if self.inject_user_data_to_request:
            setattr(request, "jsm_user_data", user_payload)
            setattr(request, "jsm_user_id", user_payload[self.user_id])

        self.user_data = user_payload
        return self.user_data

    def custom_authenticate(self, request: JsmRequest) -> tuple[UserType, str] | None:
        raise NotImplementedError("Subclasses must implement the custom_authenticate method.")

    def _validate_token(self, token: str | None, user_claim: str | None = None) -> JwtPayloadType:
        if not token:
            raise NotAuthenticated()

        self.token = token

        try:
            payload = decode_jwt_token(token)
        except jwt.DecodeError as e:
            raise InvalidToken() from e
        except jwt.ExpiredSignatureError as e:
            raise ExpiredToken() from e

        user_claim = user_claim or self.user_claim
        if user_claim not in payload:
            logger.debug("User claim %s not present in jwt", self.user_claim)
            raise AuthenticationSkipped

        return cast(JwtPayloadType, payload)

    def validate_and_inject_token_payload(self, request: JsmRequest) -> JwtPayloadType:
        token = current_jwt_token()

        payload = self._validate_token(token)

        setattr(request, "jsm_token_payload", payload)

        return payload

    def authenticate(self, request: JsmRequest) -> tuple[UserType, str] | None:
        try:
            self.validate_and_inject_token_payload(request)
            self.get_user_data(request)
            return self.custom_authenticate(request)
        except AuthenticationSkipped:
            logger.debug("Authentication %s skipped", self.__class__.__name__)
            return None


class OauthJWTAuthentication(BaseJsmAuthentication[Auth0TokenPayload, LoUser]):
    """
    Authentication class for OAuth JWT tokens.
    Should be used in DRF views that need to use Auth0 tokens.

    user_claim is set just to be explicit.
    """

    user_id: str = "user_id_auth"

    def custom_authenticate(self, request: JsmRequest) -> tuple[LoUser, str] | None:
        return (LoUser(cast(LoUserData, self.user_data)), self.token)


class LoJWTAuthentication(BaseJsmAuthentication[LvTokenPayload, LoUser]):
    """
    Authentication class for LO JWT tokens.
    Should be used in DRF views that need to use LO tokens.

    user_claim is set just to be explicit.
    """

    user_claim: str = "jsm_identity"

    identity_user_claim: str = "uid"

    @override
    def validate_and_inject_token_payload(self, request: JsmRequest) -> LvTokenPayload:
        parent_payload = super().validate_and_inject_token_payload(request)

        # Workaround to allow legacy token to be used. Will be removed in the future.
        loyalty_token = self.token
        jsm_identity_token = cast(str | None, parent_payload.get("jsm_identity"))
        payload = self._validate_token(jsm_identity_token, self.identity_user_claim)
        self.token = loyalty_token

        setattr(request, "jsm_token_payload", payload)

        return payload

    def custom_authenticate(self, request: JsmRequest) -> tuple[LoUser, str] | None:
        return (LoUser(cast(LoUserData, self.user_data)), self.token)


class LvJWTAuthentication(BaseJsmAuthentication[LvTokenPayload, LvUser]):
    """
    Authentication class for LV JWT tokens.
    Should be used in DRF views that need to use LV tokens.
    """

    user_claim: str = "uid"

    def custom_authenticate(self, request: JsmRequest) -> tuple[LvUser, str] | None:
        return (LvUser(cast(LvUserData, self.user_data)), self.token)


class LVJWTSellerAuthentication(BaseJsmAuthentication[LvTokenPayload, LvSellerUser]):

    user_claim: str = "cid"

    def get_user_data_from_server(self):
        return get_seller_user_data_from_server()

    def custom_authenticate(self, request: JsmRequest) -> tuple[LvSellerUser, str] | None:
        return (LvSellerUser(cast(LvSellerData, self.user_data)), self.token)
