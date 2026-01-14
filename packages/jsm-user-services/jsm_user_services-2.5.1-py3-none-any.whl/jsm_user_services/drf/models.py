"""
This module contains the ephemeral models for user types.

It is named this way to follow Django conventions set by AnonymousUser.
"""

from django.contrib.auth.models import AnonymousUser

from jsm_user_services.typings import BaseUserData
from jsm_user_services.typings import LoUserData
from jsm_user_services.typings import LvSellerData
from jsm_user_services.typings import LvUserData


class JsmUser(AnonymousUser):
    id = None
    pk = None
    username = ""
    is_staff = False  # It will always be False
    is_active = False  # It will always be False
    is_superuser = False  # It will always be False

    user_data: BaseUserData

    def __init__(self, *args, **kwargs) -> None:
        self.set_fields()

    def set_fields(self) -> None:
        if not self.user_data:
            return

        self.id = self.user_data["id"]
        self.pk = self.user_data["id"]
        self.username = self.user_data["name"]

    @property
    def is_authenticated(self) -> bool:
        """
        Always returns True as the Jsm User is only set if the authentication succeeds.
        """
        return True


class LoUser(JsmUser):
    user_data: LoUserData

    def __init__(self, user_data: LoUserData, *args, **kwargs) -> None:
        self.user_data = user_data
        super().__init__(*args, **kwargs)


class LvUser(JsmUser):
    user_data: LvUserData

    def __init__(self, user_data: LvUserData, *args, **kwargs) -> None:
        self.user_data = user_data
        super().__init__(*args, **kwargs)


class LvSellerUser(JsmUser):
    user_data: LvSellerData

    def __init__(self, user_data: LvSellerData, *args, **kwargs) -> None:
        self.user_data = user_data
        super().__init__(*args, **kwargs)
