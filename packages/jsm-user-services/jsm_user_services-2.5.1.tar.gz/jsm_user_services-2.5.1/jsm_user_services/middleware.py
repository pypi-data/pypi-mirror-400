import logging
import os

from typing import Callable

from django.http import HttpRequest
from django.http import HttpResponse

from jsm_user_services.services.user import get_session_id_from_bearer_token
from jsm_user_services.support.auth_jwt import get_bearer_authorization_token
from jsm_user_services.support.http_utils import convert_header_to_meta_key
from jsm_user_services.support.local_threading_utils import add_to_local_threading
from jsm_user_services.support.local_threading_utils import remove_from_local_threading
from jsm_user_services.support.string_utils import get_first_value_from_comma_separated_string

logger = logging.getLogger(__name__)

header_with_client_ip_address = convert_header_to_meta_key(os.getenv("PRIMARY_IP_ADDRESS_HEADER", "true-client-ip"))
header_with_list_of_addresses = convert_header_to_meta_key(
    os.getenv("GUNICORN_IP_ADDRESS_HEADER", "x-original-forwarded-for")
)


class JsmJwtService:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        self.process_request(request)
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_request(self, request: HttpRequest) -> None:
        add_to_local_threading("authorization_token", self._get_jwt_token_from_request(request))
        add_to_local_threading("user_ip", self._get_user_ip_from_request(request))
        add_to_local_threading("user_session_id", self._get_user_session_id_from_request(request))

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        remove_from_local_threading("authorization_token")
        remove_from_local_threading("user_ip")
        return response

    @staticmethod
    def _get_jwt_token_from_request(request: HttpRequest) -> str | None:
        """
        Extracts JWT token from a Django request object.
        """
        authorization_value = request.META.get("HTTP_AUTHORIZATION", "")
        return get_bearer_authorization_token(authorization_value)

    @staticmethod
    def _get_user_ip_from_request(request: HttpRequest) -> str | None:
        """
        Retrieve the user ip that made this request from Django HttpRequest object

        When running a service behind Akamai or other CDN solutions, it is expected that this header might contain
        a string with multiple IPs (comma separated values).
        In this case, the user's public IP that originated the request is considered to be the first one of this list.
        For reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
        """
        first_attempt_value = request.META.get(header_with_client_ip_address)
        if first_attempt_value:
            return first_attempt_value.strip()

        second_attempt_value = request.META.get(header_with_list_of_addresses)

        if not second_attempt_value:
            logger.warning("No user IP was detected!")
            return None

        return get_first_value_from_comma_separated_string(second_attempt_value)

    @staticmethod
    def _get_user_session_id_from_request(request: HttpRequest) -> str | None:
        bearer_token = JsmJwtService._get_jwt_token_from_request(request)
        if not bearer_token:
            return None
        return get_session_id_from_bearer_token(bearer_token)
