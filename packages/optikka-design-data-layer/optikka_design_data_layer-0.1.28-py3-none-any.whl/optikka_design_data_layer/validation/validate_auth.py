"""
Validate auth from event.
"""
from enum import Enum
from typing import Dict, Optional, List
from optikka_design_data_layer.logger import logger

class Role(Enum):
    """
    Role enum.
    """
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "admin"
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"

class RoleBasedPermissions:
    """
    Role based permissions.
    """
    WRITE_ROUTES: List[str] = []
    READ_ROUTES: List[str] = []
    ADMIN_ROUTES: List[str] = []
    SUPER_ADMIN_ROUTES: List[str] = []
    OPEN_ROUTES: List[str] = []

    def __init__ (
        self,
        WRITE_ROUTES: List[str],
        READ_ROUTES: List[str],
        ADMIN_ROUTES: List[str],
        OPEN_ROUTES: List[str]
    ) -> None:
        self.WRITE_ROUTES = WRITE_ROUTES
        self.READ_ROUTES = READ_ROUTES
        self.ADMIN_ROUTES = ADMIN_ROUTES
        self.OPEN_ROUTES = OPEN_ROUTES

    def is_route_allowed(self, route: str, role: Role) -> bool:
        if route in self.OPEN_ROUTES:
            return True
        elif role == Role.SUPER_ADMIN:
            return True
        elif role == Role.ADMIN:
            if route in self.ADMIN_ROUTES or route in self.READ_ROUTES or route in self.OPEN_ROUTES:
                return True
            return False
        elif role == Role.READ_WRITE:
            if route in self.READ_ROUTES or route in self.OPEN_ROUTES or route in self.WRITE_ROUTES:
                return True
            return False
        elif role == Role.READ_ONLY:
            if route in self.READ_ROUTES or route in self.OPEN_ROUTES:
                return True
            return False
        else:
            return False
        

def validate_auth_from_event(event: dict) -> Optional[Dict[str, str]]:
    """
    Validate authentication from event.
    """
    headers = event.get("headers", {})
    user_id = headers.get("x-user-id")
    if user_id is None:
        logger.error("User ID is required")
        return None
    studio_id = headers.get("x-studio-id")
    if studio_id is None:
        logger.error("Studio ID is required")
        return None
    account_id = headers.get("x-account-id")
    if account_id is None:
        logger.error("Account ID is required")
        return None
    role = headers.get("x-role")
    if role is None:
        logger.error("Role ID is required")
        return None

    #retrun user information as a dictionary
    return {
        "user_id": user_id,
        "studio_id": studio_id,
        "account_id": account_id,
        "role": role
    }
