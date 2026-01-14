import re

from typing import Optional

import jwt

from jsm_user_services import settings


def decode_jwt_token(jwt_token: str) -> dict:
    """
    Gets a decoded JWT token with the HS256 algorithm.
    """
    if not settings.JSM_JWT_DECODE:
        return {}

    options = {"verify_exp": True}
    kwargs = {}

    if settings.JSM_JWT_ALGORITHM:
        kwargs["algorithms"] = [settings.JSM_JWT_ALGORITHM]

    if settings.JSM_JWT_AUDIENCE:
        kwargs["audience"] = settings.JSM_JWT_AUDIENCE

    if not settings.JSM_JWT_SHOULD_VERIFY_SIGNATURE:
        options["verify_signature"] = False
    else:
        options["verify_signature"] = True
        kwargs["key"] = settings.JSM_JWT_SECRET_KEY

    return jwt.decode(jwt_token, options=options, **kwargs)


def get_bearer_authorization_token(authorization_value: str) -> Optional[str]:
    """
    Retrieve a bearer authorization token from an Authorization header value.

    It expects the header value to be something on the lines of: "Bearer token".

    Examples:
    - get_bearer_authorization_token("Bearer token") # returns "token"
    - get_bearer_authorization_token("bearer token") # returns None
    - get_bearer_authorization_token("Token token") # returns None
    - get_bearer_authorization_token("whatever") # returns None
    """
    match = re.match("Bearer", authorization_value)

    if not match:
        return None

    auth_type_beginning = match.span()[1]
    jwt_token = authorization_value[auth_type_beginning:].strip()

    return jwt_token
