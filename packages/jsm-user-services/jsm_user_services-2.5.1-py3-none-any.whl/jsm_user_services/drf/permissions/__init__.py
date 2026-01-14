# Base helpers
from jsm_user_services.drf.permissions.base import protected
from jsm_user_services.drf.permissions.lo import ActiveUserPermission
from jsm_user_services.drf.permissions.lo import AnyLoggedUserPermission
from jsm_user_services.drf.permissions.lo import EmployeeOrManagerUserPermission
from jsm_user_services.drf.permissions.lo import EmployeeUserPermission
from jsm_user_services.drf.permissions.lo import GoogleRecaptchaPermission
from jsm_user_services.drf.permissions.lo import IndustrySellerUserPermission
from jsm_user_services.drf.permissions.lo import IsUserAllowedToPermission
from jsm_user_services.drf.permissions.lo import LoggedUserOauthAndLegacyPermission
from jsm_user_services.drf.permissions.lo import ManagerUserPermission
from jsm_user_services.drf.permissions.lo import OauthUserPermission
from jsm_user_services.drf.permissions.lo import OwnerOrManagerUserPermission
from jsm_user_services.drf.permissions.lo import OwnerUserPermission
from jsm_user_services.drf.permissions.lo import PendingValidationUserPermission
from jsm_user_services.drf.permissions.lo import RetailUserPermission
from jsm_user_services.drf.permissions.lo import RoleBasedPermission
from jsm_user_services.drf.permissions.lo import StatusBasedPermission
from jsm_user_services.drf.permissions.lo import UserBlockedByCpfAndBirthDateValidationFailedPermission
from jsm_user_services.drf.permissions.lv import LVAdminJsmAdminPermission
from jsm_user_services.drf.permissions.lv import LVAdminSellerAdminPermission
from jsm_user_services.drf.permissions.lv import LVAdminSellerApiPermission
from jsm_user_services.drf.permissions.lv import LVAdminSellerCoordinatorPermission
from jsm_user_services.drf.permissions.lv import LVAdminSellerSalesmanPermission
from jsm_user_services.drf.permissions.lv import LVBasePermission
from jsm_user_services.drf.permissions.lv import LVClientBuyerPermission
from jsm_user_services.drf.permissions.lv import LVClientJsmAdminPermission
from jsm_user_services.drf.permissions.lv import LVClientSellerAdminPermission
from jsm_user_services.drf.permissions.lv import LVClientSellerApiPermission
from jsm_user_services.drf.permissions.lv import LVClientSellerCoordinatorPermission
from jsm_user_services.drf.permissions.lv import LVClientSellerSalesmanPermission

__all__ = [
    # Base helpers
    "protected",
    # LO Permissions
    "AnyLoggedUserPermission",
    "EmployeeOrManagerUserPermission",
    "EmployeeUserPermission",
    "GoogleRecaptchaPermission",
    "IndustrySellerUserPermission",
    "IsUserAllowedToPermission",
    "LoggedUserOauthAndLegacyPermission",
    "ManagerUserPermission",
    "OauthUserPermission",
    "OwnerOrManagerUserPermission",
    "OwnerUserPermission",
    "RetailUserPermission",
    "ActiveUserPermission",
    "PendingValidationUserPermission",
    "RoleBasedPermission",
    "StatusBasedPermission",
    "UserBlockedByCpfAndBirthDateValidationFailedPermission",
    # LV Permissions
    "protected",
    "LVBasePermission",
    "LVAdminJsmAdminPermission",
    "LVClientJsmAdminPermission",
    "LVClientBuyerPermission",
    "LVAdminSellerAdminPermission",
    "LVClientSellerAdminPermission",
    "LVAdminSellerApiPermission",
    "LVClientSellerApiPermission",
    "LVAdminSellerCoordinatorPermission",
    "LVClientSellerCoordinatorPermission",
    "LVAdminSellerSalesmanPermission",
    "LVClientSellerSalesmanPermission",
]
