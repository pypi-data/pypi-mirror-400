import hashlib

from importlib import import_module
from typing import Any
from typing import List
from typing import Optional

import jwt

from jsm_user_services import settings
from jsm_user_services.support.auth_jwt import decode_jwt_token
from jsm_user_services.support.http_utils import get_response_body
from jsm_user_services.support.http_utils import request
from jsm_user_services.support.local_threading_utils import get_from_local_threading
from jsm_user_services.support.request_id import current_request_id
from jsm_user_services.support.request_id import request_id_header_name


def jwt_has_required_roles(jwt_required_roles: List[str], assert_all=True) -> bool:
    """
    Asserts that the jwt token has all the required roles.
    """
    jsm_token_data = get_jsm_user_data_from_jwt()

    if not jsm_token_data:
        return False

    try:
        jwt_token_roles = jsm_token_data["roles"]
    except KeyError:
        return False

    if not jwt_token_roles:
        return False

    if assert_all:
        return all((jwt_token_role in jwt_required_roles) for jwt_token_role in jwt_token_roles)

    return any((jwt_token_role in jwt_required_roles) for jwt_token_role in jwt_token_roles)


def current_jwt_token() -> Optional[str]:
    return get_from_local_threading("authorization_token")


def get_jwt_algorithm() -> str:
    """
    Retrieves the algorithm used in the JWT token.
    """
    token = current_jwt_token()
    header = jwt.get_unverified_header(token)
    return header.get("alg")


def get_jsm_token() -> Optional[str]:
    token = current_jwt_token()
    if token:
        return decode_jwt_token(token)["jsm_identity"]

    return None


def get_oauth_token() -> Optional[dict[Any, Any]]:
    """
    This function retrieves the OAuth token from the local threading.
    If the token is not present, it returns None.
    """
    token = current_jwt_token()
    if token:
        return decode_jwt_token(token)
    return None


def get_jsm_user_data_from_jwt() -> Optional[dict]:
    token = get_jsm_token()

    if token:
        return decode_jwt_token(token)

    return None


def get_user_email_from_jwt() -> Optional[str]:
    user_data = get_jsm_user_data_from_jwt()
    if user_data:
        return user_data.get("email")

    return None


def get_user_id_from_jwt() -> Optional[str]:
    user_data = get_jsm_user_data_from_jwt()
    if user_data:
        return user_data.get("uid")

    return None


def get_user_access_as_id_from_jwt() -> Optional[str]:
    user_data = get_jsm_user_data_from_jwt()
    if user_data:
        return user_data.get("fid", None)

    return None


def get_user_data_from_server() -> dict:
    current_token = current_jwt_token()
    headers = {request_id_header_name: current_request_id()}
    user_url = settings.USER_API_HOST
    user_data_endpoint = settings.USER_API_PROFILE_ENDPOINT

    if current_token:
        headers["Authorization"] = f"Bearer {current_jwt_token()}"

    with request() as r:
        response = r.get(f"{user_url}{user_data_endpoint}", headers=headers)
        return get_response_body(response)


def get_user_data_from_cpf(cpf: str) -> dict:
    current_token = current_jwt_token()
    headers = {request_id_header_name: current_request_id()}
    user_url = settings.USER_API_HOST

    if current_token:
        headers["Authorization"] = f"Bearer {current_jwt_token()}"

    with request() as r:
        response = r.get(f"{user_url}/v1/users/search?cpf={cpf}", headers=headers)
        return get_response_body(response)


def get_user_data_from_id(user_id: str) -> dict:
    current_token = current_jwt_token()
    headers = {request_id_header_name: current_request_id()}
    user_url = settings.USER_API_HOST

    if current_token:
        headers["Authorization"] = f"Bearer {current_jwt_token()}"

    with request() as r:
        response = r.get(f"{user_url}/v1/users/{user_id}/", headers=headers)

        return get_response_body(response)


def get_cpf_from_jwt() -> Optional[str]:
    email = get_user_email_from_jwt()

    return email.split("@")[0] if email else None


def is_retail_user(user_id: str) -> bool:
    settings = import_module("jsm_user_services.settings")
    user_api_token = settings.USER_API_TOKEN
    user_url = settings.USER_API_HOST

    headers = {request_id_header_name: current_request_id(), "Authorization": f"Token {user_api_token}"}

    with request() as r:
        response = r.get(f"{user_url}/v1/users/search/?user_id_ref={user_id}&is_retail_user=True", headers=headers)
        response_content = get_response_body(response)
    return response_content["count"] == 1


def get_user_ip() -> Optional[str]:
    return get_from_local_threading("user_ip")


def get_session_id_from_bearer_token(bearer_token: str) -> str:
    return hashlib.sha1(bearer_token.encode("utf-8")).hexdigest()


def get_user_session_id() -> Optional[str]:
    return get_from_local_threading("user_session_id")


def get_user_id_auth() -> Optional[str]:
    """
    This function retrieves the user's ID from an OAuth JWT token.
    If the "sub" field is not present, it returns None.
     Note:
        If the claim "https://login.juntossomosmais.com.br/user_id_auth" is present in the JWT from Auth0, it indicates
        that the main information in the token belongs to the Central user (not the actual user).
        Therefore, we must return the user_id_auth, as this is the ID that represents the real user.
    """
    user_data = get_oauth_token()

    if not user_data:
        return None

    return user_data.get("https://login.juntossomosmais.com.br/user_id_auth") or user_data.get("sub")


def get_user_email_from_oauth_jwt() -> Optional[str]:
    """
    This function retrieves the user's email from an OAuth JWT token.
    If the "email" field is not present, it returns None.

    Note:
        If the claim "https://login.juntossomosmais.com.br/user_id_auth" is present in the JWT from Auth0, it indicates
        that the main information in the token belongs to the Central user (not the actual user).
        Therefore, we must return None in this case, as the email does not represent the real user.

    """
    user_data = get_oauth_token()

    if not user_data or user_data.get("https://login.juntossomosmais.com.br/user_id_auth"):
        return None

    return user_data.get("email")


def get_user_id_auth_or_user_id_ref_in_jwt() -> Optional[str]:
    """
    Retrieves the user_id_auth or user_id_ref from the JWT token according to the algorithm used.
    """
    alg = get_jwt_algorithm()

    alg_to_user_id_map = {"RS256": get_user_id_auth, "HS256": get_user_id_from_jwt}

    return alg_to_user_id_map.get(alg, lambda: None)()


def get_seller_user_data_from_server() -> dict:
    current_token = current_jwt_token()
    headers = {request_id_header_name: current_request_id()}

    if not current_token:
        raise ValueError("No current token found")

    headers["Authorization"] = f"Bearer {current_jwt_token()}"

    with request() as r:
        response = r.get(f"{settings.USER_API_HOST}{settings.USER_API_SELLER_PROFILE_ENDPOINT}", headers=headers)
        response_body = get_response_body(response)
        return {
            "id": response_body[0],
            "seller_id": response_body[0],
            "name": "",
        }
