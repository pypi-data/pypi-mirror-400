from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Token is invalid or expired"
    default_code = "TOKEN_NOT_VALID"


class ExpiredToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Token is expired"
    default_code = "TOKEN_EXPIRED"


class NotAuthenticated(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication credentials were not provided."
    default_code = "NOT_AUTHENTICATED"


class AuthenticationSkipped(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication was skipped"
    default_code = "AUTHENTICATION_SKIPPED"
