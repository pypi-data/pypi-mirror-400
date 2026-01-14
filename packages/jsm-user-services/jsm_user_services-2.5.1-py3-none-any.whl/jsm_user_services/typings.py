from typing import List
from typing import Literal
from typing import NotRequired
from typing import Optional
from typing import Protocol
from typing import TypedDict
from uuid import UUID

from jsm_user_services.enums import LVApplication
from jsm_user_services.enums import LVUserRole


# Jsm Request Protocol
class JsmRequest(Protocol):
    jsm_token_payload: dict
    jsm_user_id: str
    jsm_user_data: dict


class Claim(TypedDict):
    key: str
    value: str


class BaseUserData(TypedDict):
    id: str
    name: str


# Auth0 Token Payload
class Auth0TokenPayload(TypedDict):
    client_id: str  # Client ID
    session_id: str  # Session ID
    user_id_auth: str  # User ID Auth, usually means that this token is being impersonated.
    iss: str  # Issuer
    sub: str  # Subject
    aud: list[str]  # Audience
    iat: int  # Issued at
    exp: int  # Expiration time
    scope: str  # Scope, separated by spaces
    azp: str  # Authorized party


# Lv Token Payload
class LvTokenPayload(TypedDict):
    email: str
    unique_name: str
    website: LVApplication
    uid: str | UUID
    role: LVUserRole
    nbf: int  # Token not valid before time
    exp: int  # Expiration time
    iat: int  # Issued at
    iss: str  # Issuer
    aud: str  # Audience
    fid: NotRequired[str | UUID | None]  # Federated ID
    sellers: NotRequired[str | UUID | list[str | UUID] | None]  # Sellers ID
    cnpjs: NotRequired[str | list[str] | None]  # CNPJs


# Lo Token Payload
class LoTokenPayload(TypedDict):
    """
    Legacy token payload for LO. This token is a wrapper for Lv Token Payload.
    If needed, use the info inside jsm_identity.
    """

    token_type: Literal["access"]
    exp: int  # Expiration time
    iat: int  # Issued at
    jti: str  # JWT ID
    jsm_identity: str  # Lv Token Payload


# Lo User Data
class Email(TypedDict):
    type: str
    email: str


class Phone(TypedDict):
    type: str
    number: str


class BlockedReason(TypedDict):
    reason: str
    blocked_date: str


class LoUserData(BaseUserData):
    cpf: str
    roles: List[str]
    emails: List[Email]
    gender: str
    phones: List[Phone]
    status: str
    mediums: NotRequired[List[str]]
    birthday: str
    username: str
    addresses: NotRequired[List[dict]]
    occupation: str
    blocked_reason: NotRequired[BlockedReason | None]
    not_allowed_to: NotRequired[List[str]]
    registered_date: str
    industry_register_helper: NotRequired[str]
    segments: List[str] | None
    user_id_auth: str | None


# Lv User Data
class LvUserData(BaseUserData):
    email: str
    cnpj: str
    cpf: str
    gender: int
    cep: NotRequired[Optional[str]]
    street: NotRequired[Optional[str]]
    complement: NotRequired[Optional[str]]
    phoneNumber: NotRequired[Optional[str]]
    neighbourhood: NotRequired[Optional[str]]
    state: int
    city: NotRequired[Optional[str]]
    mobile: NotRequired[Optional[str]]
    number: NotRequired[Optional[str]]
    twoFactorEnabled: bool
    uf: str
    metadata: NotRequired[Optional[str]]
    claims: List[Claim]
    roles: List[str]
    sellers: List[str]
    permissions: List[str]
    cnpjs: List[str]
    cpfs: List[str]
    fidRoles: NotRequired[Optional[List[str]]]
    isJSMAdmin: bool


class LvUserDataResponse(TypedDict):
    data: LvUserData
    success: bool


class LvSellerData(BaseUserData):
    """Seller user data for LV JWT authentication."""

    seller_id: str
