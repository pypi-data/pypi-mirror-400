from enum import Enum


# LV Enums
class LVApplication(Enum):
    CLIENT_APPLICATION = "ClientApplication"  # Public application, used by customers.
    ADMIN_APPLICATION = "AdminApplication"  # Admin application, used by admins.


class LVUserRole(Enum):
    # Seller and industry terms are interchangeable in this context.
    JSM_ADMIN = "JSMAdmin"  # JSM Full admin role, used by JSM users. Used to manage everything in the system.
    BUYER = "MasterClient"  # Customer role, used by customers. This is the default role for customers.
    SELLER_ADMIN = "MasterAdmin"  # Seller Admin role, used by sellers. Used to manage seller data in admin.
    SELLER_API = "Admin"  # API role. Used by sellers to access the API.
    SELLER_COORDINATOR = (
        "Coordinator"  # Coordinator role, used by sellers to manage some things in the seller in admin.
    )
    CUSTOMER = "Customer"  # Customer role, used mainly by loyalty jwt.
    SELLER_SALESMAN = "Salesman"  # Salesman role, used by sellers to sell products.
