"""
Module with useful user permissions classes meant to be used with Django Rest Framework.
"""

import logging

from typing import Any
from typing import List
from typing import Optional
from typing import Type

from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework.request import Request

from jsm_user_services.drf.helpers import AllowClassBehaviorAsFunction
from jsm_user_services.drf.helpers import is_exception_related_to_api_exception
from jsm_user_services.drf.permissions.base import JSMUserBasePermission
from jsm_user_services.exception import IncorrectTypePermissionConfiguration
from jsm_user_services.services.google import perform_recaptcha_validation
from jsm_user_services.services.user import get_jwt_algorithm
from jsm_user_services.services.user import get_user_id_auth
from jsm_user_services.services.user import get_user_id_auth_or_user_id_ref_in_jwt

logger = logging.getLogger(__name__)


class StatusBasedPermission(JSMUserBasePermission):
    """
    Base class for the status-based permissions. Implements methods for validating requests against
    the user micro service and an utility method that asserts that the user has the appropriate status.
    """

    @classmethod
    def _validate_user_status(cls, request: Request, allowed_status: List[str]):
        """
        Validates if the user has the appropriate status against the allowed status.
        """
        append_user_data_to_request = cls.APPEND_USER_DATA
        user_data = cls._validate_request_against_user_service(
            request, append_user_data_to_request=append_user_data_to_request
        )

        if "status" not in user_data:
            return False

        return user_data["status"] in allowed_status

    @classmethod
    def _validate_user_blocked_reason(cls, request: Request, blocked_reasons: List[str]):
        """
        Validates if the user has the appropriate blocked reason against the allowed blocked reasons.
        """
        append_user_data_to_request = cls.APPEND_USER_DATA
        user_data = cls._validate_request_against_user_service(
            request, append_user_data_to_request=append_user_data_to_request
        )

        if not user_data.get("blocked_reason") or not user_data["blocked_reason"].get("reason"):
            return False

        return user_data["blocked_reason"]["reason"] in blocked_reasons


class ActiveUserPermission(StatusBasedPermission):
    """
    Permission that allows only users which the status is 'active'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user status is 'active'.
        """
        return self._validate_user_status(request, allowed_status=["active"])


class PendingValidationUserPermission(StatusBasedPermission):
    """
    Permission that allows only users which the status is 'pending-validation'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user status is 'pending-validation'.
        """
        return self._validate_user_status(request, allowed_status=["pending-validation"])


class UserBlockedByCpfAndBirthDateValidationFailedPermission(StatusBasedPermission):
    """
    Permission that allows only users which the status is 'blocked' and
    blocked reason is 'cpf-birth-date-validation-failed'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user status is 'blocked' and blocked reason is 'cpf-birth-date-validation-failed'.
        """
        return self._validate_user_status(request, allowed_status=["blocked"]) and self._validate_user_blocked_reason(
            request, blocked_reasons=["cpf-birth-date-validation-failed"]
        )


class RoleBasedPermission(JSMUserBasePermission):
    """
    Base class for the role-based permissions. Implements methods for validating requests against
    the user micro service and an utility method that asserts that the user has the appropriate role.
    """

    @classmethod
    def _validate_user_role(cls, request: Request, allowed_roles: List[str]):
        """
        Validates if the user has the appropriate role against the allowed roles.
        """
        append_user_data_to_request = cls.APPEND_USER_DATA
        user_data = cls._validate_request_against_user_service(
            request, append_user_data_to_request=append_user_data_to_request
        )
        user_roles: List[str] = user_data.get("roles", [])
        if not user_roles:
            return False

        return any(user_role in allowed_roles for user_role in user_roles)


class RetailUserPermission(RoleBasedPermission, ActiveUserPermission):
    """
    Permission that allows only active users with the roles 'owner', 'manager' or 'employee'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is an active owner, manager or employee.
        """
        is_user_active = ActiveUserPermission.has_permission(self, request, view)
        has_retail_role = self._validate_user_role(request, allowed_roles=["owner", "employee", "manager"])
        return is_user_active and has_retail_role


class EmployeeOrManagerUserPermission(RoleBasedPermission, ActiveUserPermission):
    """
    Permission that allows only active users with the role 'employee' or 'manager'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is an active employee or manager.
        """
        is_user_active = ActiveUserPermission.has_permission(self, request, view)
        has_employee_or_manager_role = self._validate_user_role(request, allowed_roles=["employee", "manager"])
        return is_user_active and has_employee_or_manager_role


class OwnerOrManagerUserPermission(RoleBasedPermission, ActiveUserPermission):
    """
    Permission that allows only active users with the role 'owner' or 'manager'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is an active owner or manager.
        """
        is_user_active = ActiveUserPermission.has_permission(self, request, view)
        has_owner_or_manager_role = self._validate_user_role(request, allowed_roles=["manager", "owner"])
        return is_user_active and has_owner_or_manager_role


class ManagerUserPermission(RoleBasedPermission, ActiveUserPermission):
    """
    Permission that allows only active users with the role 'manager'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is an active manager.
        """
        is_user_active = ActiveUserPermission.has_permission(self, request, view)
        has_manager_role = self._validate_user_role(request, allowed_roles=["manager"])
        return is_user_active and has_manager_role


class EmployeeUserPermission(RoleBasedPermission, ActiveUserPermission):
    """
    Permission that allows only active users with the role 'employee'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is an active employee.
        """
        is_user_active = ActiveUserPermission.has_permission(self, request, view)
        has_employee_role = self._validate_user_role(request, allowed_roles=["employee"])
        return is_user_active and has_employee_role


class OwnerUserPermission(RoleBasedPermission, ActiveUserPermission):
    """
    Permission that allows only active users with the role 'owner'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is an active owner.
        """
        is_user_active = ActiveUserPermission.has_permission(self, request, view)
        has_owner_role = self._validate_user_role(request, allowed_roles=["owner"])
        return is_user_active and has_owner_role


class IndustrySellerUserPermission(RoleBasedPermission, ActiveUserPermission):
    """
    Permission that allows only active users with the role 'industry-seller'.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user is an active industry seller.
        """
        is_user_active = ActiveUserPermission.has_permission(self, request, view)
        has_industry_seller_role = self._validate_user_role(request, allowed_roles=["industry-seller"])
        return is_user_active and has_industry_seller_role


class AnyLoggedUserPermission(RoleBasedPermission, ActiveUserPermission):
    """
    Permission that allows active users to access the requested resource regardless
    of their roles as long as they have a VALID, NON EXPIRED JSM JWT.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the active user is just logged in with a valid jwt (non expired).
        """
        is_user_active = ActiveUserPermission.has_permission(self, request, view)
        has_valid_role = self._validate_user_role(
            request, allowed_roles=["industry-seller", "employee", "manager", "owner"]
        )
        return is_user_active and has_valid_role


class GoogleRecaptchaPermission(permissions.BasePermission, AllowClassBehaviorAsFunction):
    """
    A permission class which checks if the request is authorized by Google Recaptcha V3.

    In order to use it, the request must have the key "g_recaptcha_response" or "g-recaptcha-response" on the request's
    body or header. Otherwise the request won't be authorized without even checking it on Google.

    Just be aware that a header with underscore is not allowed. So do not use the key "g_recaptcha_response"
    on the header.
    """

    def __init__(self, exception_in_case_of_failed: Optional[APIException | Type[APIException]] = None):
        """
        Sets the default value for "exception_in_case_of_failed_verification" property. It will be used to return
        a custom response, in case of this permission fails.
        This exception must inherit APIException, from rest_framework.exceptions, otherwise it will be ignored.
        """

        self.exception_in_case_of_failed_verification = exception_in_case_of_failed

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Retrieves the Google data on the request and then performs a request to Google, in order to check if the
        received data is valid or not.
        """

        g_recaptcha_response = self._retrieve_g_recaptcha_response(request)
        use_received_exception = is_exception_related_to_api_exception(self.exception_in_case_of_failed_verification)

        # preventing an unnecessary request to Google, since key is not defined
        if not g_recaptcha_response:
            if use_received_exception:
                raise self.exception_in_case_of_failed_verification  # type: ignore
            return False

        google_response: bool = perform_recaptcha_validation(g_recaptcha_response)

        if not google_response and use_received_exception:
            # raising an APIException that will return the customized response
            raise self.exception_in_case_of_failed_verification  # type: ignore

        return google_response

    @classmethod
    def _retrieve_g_recaptcha_response(cls, request: Request) -> Optional[str]:
        """
        Lookup on the request's body and header in order to retrieve the recaptcha key.

         If the same key is present on header and body, the header data will be overridden by the body value.
         Also, if both keys are present, the priority is "g_recaptcha_response" over "g-recaptcha-response".
        """

        expected_keys = ["g_recaptcha_response", "g-recaptcha-response"]

        for key in expected_keys:
            key_value = request.data.get(key) or request.headers.get(key)
            if key_value:
                return key_value
        return None


class IsUserAllowedToPermission(JSMUserBasePermission, AllowClassBehaviorAsFunction):
    """
    A permission class which checks if user is authorized to execute an action based on 'not_allowed_to' parameter.
    Implements methods for validating requests against the user micro service and an utility method that asserts
    the user has the appropriate permission for to do, or not to do, a determined action.

    Example:
        class SomeAwesomeView():
            permission_classes = [
                IsUserAllowedToPermission(
                    ["redeem", "score"], full_match=False, exception_in_case_of_failed=CustomExceptionNotAllowedTo
                )
            ]

        In this example, the custom exception should be implemented into your own project.
    """

    def __init__(
        self,
        not_allowed_to: List[str],
        full_match: bool = False,
        exception_in_case_of_failed: Optional[APIException | Type[APIException]] = None,
    ):
        """
        Sets the default value for "exception_in_case_of_failed_verification" property. It will be used to return
        a custom response, in case of this permission fails. This exception must inherit APIException,
        from rest_framework.exceptions, otherwise it will be ignored.

        Full match property indicates that user data must contains all the 'not_allowed_to' defined parameters.
        On the other hand, if full match is equal to False, the permission class checks
        if user data contains any of the 'not_allowed_to' parameters.
        """

        self.exception_in_case_of_failed_verification = exception_in_case_of_failed
        self.full_match = full_match

        if not isinstance(not_allowed_to, list):
            logger.error(
                f"Permission class 'IsUserAllowedToPermission' expected 'List[str]', got  {type(not_allowed_to)}"
            )
            raise IncorrectTypePermissionConfiguration(f"Expected type 'List[str]', got {type(not_allowed_to)} instead")

        self.not_allowed_to = not_allowed_to

    @classmethod
    def _verify_if_user_should_be_allowed(
        cls, request: Request, not_allowed_actions: List[str], full_match: bool
    ) -> bool:
        """
        Validates 'not_allowed_to' user parameter against the 'not_allowed_actions' permission class parameter.
        """

        append_user_data_to_request = cls.APPEND_USER_DATA
        user_data = cls._validate_request_against_user_service(
            request, append_user_data_to_request=append_user_data_to_request
        )
        user_not_allowed_to: List[str] = user_data.get("not_allowed_to", [])

        set_from_not_allowed_actions = set(not_allowed_actions)
        set_from_user_not_allowed_to = set(user_not_allowed_to)
        intersected_actions = set_from_not_allowed_actions.intersection(set_from_user_not_allowed_to)

        if not (user_not_allowed_to or intersected_actions):
            return True

        if full_match:
            return len(intersected_actions) != len(set_from_not_allowed_actions)
        return not bool(intersected_actions)

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Asserts that the user hasn't an action restriction against the 'not_allowed_to' permission class parameter.
        """

        use_received_exception: bool = is_exception_related_to_api_exception(
            self.exception_in_case_of_failed_verification
        )

        is_allowed: bool = self._verify_if_user_should_be_allowed(
            request,
            not_allowed_actions=self.not_allowed_to,
            full_match=self.full_match,
        )

        if use_received_exception and not is_allowed:
            raise self.exception_in_case_of_failed_verification  # type: ignore

        return is_allowed


class LoggedUserOauthAndLegacyPermission(JSMUserBasePermission):
    """
    Permission to check if the user is authenticated with an Oauth or Loyalty JWT.
    """

    def has_permission(self, request, *args, **kwargs):
        alg = get_jwt_algorithm()
        if alg == "RS256":
            user = get_user_id_auth_or_user_id_ref_in_jwt()
            return bool(user)
        else:
            return bool(request.user and request.user.is_authenticated)


class OauthUserPermission(JSMUserBasePermission):
    """
    Permission to check if the user is authenticated with an Oauth JWT.
    """

    def has_permission(self, request, *args, **kwargs):
        user = get_user_id_auth()
        return bool(user)
