"""
This file contains the permissions for the LV Django Apps.

Roles here are denormalized for easier use. Key being OUR name and values being the actual role name from identity.

Permissions ready to be used:

[JSM Admin]
- LVAdminJsmAdminPermission -> Admin app / Active User / Roles: JSMAdmin
- LVClientJsmAdminPermission -> Client app / Active User / Roles: JSMAdmin

[Buyer/Customer]
- LVClientBuyerPermission -> Client app / Active User / Roles: MasterClient

[Seller/Industry (Online and Offline) Admin]
- LVAdminSellerAdminPermission -> Admin app / Active User / Roles: MasterAdmin
- LVClientSellerAdminPermission -> Client app / Active User / Roles: MasterAdmin

[Seller/Industry (Online and Offline) API]
- LVAdminSellerApiPermission -> Admin app / Active User / Roles: Admin
- LVClientSellerApiPermission -> Client app / Active User / Roles: Admin

[Seller/Industry (Online and Offline) Coordinator]
- LVAdminSellerCoordinatorPermission -> Admin app / Active User / Roles: Coordinator
- LVClientSellerCoordinatorPermission -> Client app / Active User / Roles: Coordinator

[Seller/Industry (Online and Offline) Salesman]
- LVAdminSellerSalesmanPermission -> Admin app / Active User / Roles: Salesman
- LVClientSellerSalesmanPermission -> Client app / Active User / Roles: Salesman
"""

import logging

from typing import Any

from rest_framework.request import Request

from jsm_user_services.drf.permissions.base import JSMUserBasePermission
from jsm_user_services.enums import LVApplication
from jsm_user_services.enums import LVUserRole

logger = logging.LoggerAdapter(logging.getLogger(__name__), {"prefix": "JSM_USER_SERVICES"})


# Base permissions
class LVBasePermission(JSMUserBasePermission):
    """
    Base permission for LV Django Apps.
    """

    sources: set[LVApplication] = set()
    roles: set[LVUserRole] = set()

    _decoded_jwt_token: dict | None = None
    _decoded_jwt_token_keys: set[str] = set()
    _allowed_sources_set: set[str] = set()
    _allowed_roles_set: set[str] = set()

    _failed_validation: bool = False

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._allowed_sources_set = {source.value.lower() for source in self.sources}
        self._allowed_roles_set = {role.value.lower() for role in self.roles}

    def _is_valid(self, request: Request, key: str, value_to_check: set[str], **kwargs: Any) -> bool:
        if self._failed_validation:
            logger.debug("Validation already failed, skipping %s permission", key)
            return False

        logger.debug("Checking %s permission", key)
        decoded_token, _ = self.decode_jwt_token(request)

        if isinstance(decoded_token[key], list):
            token_set = {token_value.lower() for token_value in decoded_token[key]}
        else:
            token_set = {decoded_token[key].lower()}

        is_allowed_value = value_to_check.intersection(token_set)

        logger.debug("%s is allowed: %s", key, is_allowed_value)

        return bool(is_allowed_value)

    def has_permission(self, request: Request, view: Any) -> bool:
        logger.debug("Checking permissions")
        is_valid = super().has_permission(request, view)

        if is_valid and self.sources:
            is_valid = self._is_valid(request, "website", self._allowed_sources_set)
        if is_valid and self.roles:
            is_valid = self._is_valid(request, "role", self._allowed_roles_set)

        return is_valid


# Sources permissions
class LVAdminPermission(LVBasePermission):
    """
    Permission for LV Admin Apps for users with Source role.
    """

    sources: set[LVApplication] = {LVApplication.ADMIN_APPLICATION}


class LVClientPermission(LVBasePermission):
    """
    Permission for LV Client Apps for users with Source role.
    """

    sources: set[LVApplication] = {LVApplication.CLIENT_APPLICATION}


# JsmAdmin permissions
class LVAdminJsmAdminPermission(LVAdminPermission):
    """
    Permission for LV Admin Apps for users with JSM Admin role.
    """

    roles: set[LVUserRole] = {LVUserRole.JSM_ADMIN}


class LVClientJsmAdminPermission(LVClientPermission):
    """
    Permission for LV Client Apps for users with JSM Admin role.
    """

    roles: set[LVUserRole] = {LVUserRole.JSM_ADMIN}


# Buyer permissions
class LVClientBuyerPermission(LVClientPermission):
    """
    Permission for LV Admin Apps for users with Buyer role.
    """

    roles: set[LVUserRole] = {LVUserRole.BUYER}


# Seller (Industry) permissions
class LVAdminSellerAdminPermission(LVAdminPermission):
    """
    Permission for LV Admin Apps for users with Seller Admin role.
    """

    roles: set[LVUserRole] = {LVUserRole.SELLER_ADMIN}


class LVClientSellerAdminPermission(LVClientPermission):
    """
    Permission for LV Client Apps for users with Seller Admin role.
    """

    roles: set[LVUserRole] = {LVUserRole.SELLER_ADMIN}


# Seller API permissions
class LVAdminSellerApiPermission(LVAdminPermission):
    """
    Permission for LV Admin Apps for users with Seller API role.
    """

    roles: set[LVUserRole] = {LVUserRole.SELLER_API}


class LVClientSellerApiPermission(LVClientPermission):
    """
    Permission for LV Client Apps for users with Seller API role.
    """

    roles: set[LVUserRole] = {LVUserRole.SELLER_API}


# Seller Coordinator permissions
class LVAdminSellerCoordinatorPermission(LVAdminPermission):
    """
    Permission for LV Admin Apps for users with Seller Coordinator role.
    """

    roles: set[LVUserRole] = {LVUserRole.SELLER_COORDINATOR}


class LVClientSellerCoordinatorPermission(LVClientPermission):
    """
    Permission for LV Client Apps for users with Seller Coordinator role.
    """

    roles: set[LVUserRole] = {LVUserRole.SELLER_COORDINATOR}


# Seller Salesman permissions
class LVAdminSellerSalesmanPermission(LVAdminPermission):
    """
    Permission for LV Admin Apps for users with Seller Salesman role.
    """

    roles: set[LVUserRole] = {LVUserRole.SELLER_SALESMAN}


class LVClientSellerSalesmanPermission(LVClientPermission):
    """
    Permission for LV Client Apps for users with Seller Salesman role.
    """

    roles: set[LVUserRole] = {LVUserRole.SELLER_SALESMAN}
