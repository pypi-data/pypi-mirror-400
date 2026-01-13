from typing import Callable

from strawberry.types import Info

# Type alias for permission checker functions
PermissionChecker = Callable[[Info], bool]


def is_authenticated(info: Info) -> bool:
    """
    Check if user is authenticated.

    Expects info.context["user"] to be set and not "anonymous".
    """
    if not hasattr(info, "context") or info.context is None:
        return False
    user = info.context.get("user")
    return user is not None and user != "anonymous"


def is_admin(info: Info) -> bool:
    """
    Check if user has admin role.

    Expects info.context["roles"] to contain "admin".
    """
    if not hasattr(info, "context") or info.context is None:
        return False
    roles = info.context.get("roles", [])
    if roles is None:
        return False
    return "admin" in roles


def has_role(role: str) -> PermissionChecker:
    """
    Create a permission checker for a specific role.

    Args:
        role: Role name to check for

    Returns:
        Permission checker function

    Example:
        permissions = {
            "delete": has_role("admin"),
            "create": has_role("editor")
        }
    """

    def checker(info: Info) -> bool:
        if not hasattr(info, "context") or info.context is None:
            return False
        roles = info.context.get("roles", [])
        if roles is None:
            return False
        return role in roles

    return checker


def has_any_role(*required_roles: str) -> PermissionChecker:
    """
    Check if user has any of the specified roles.

    Example:
        permissions = {"delete": has_any_role("admin", "moderator")}
    """

    def checker(info: Info) -> bool:
        if not hasattr(info, "context") or info.context is None:
            return False
        roles = info.context.get("roles", [])
        if roles is None:
            return False
        return any(role in roles for role in required_roles)

    return checker


def has_all_roles(*required_roles: str) -> PermissionChecker:
    """
    Check if user has all of the specified roles.

    Example:
        permissions = {"delete": has_all_roles("admin", "verified")}
    """

    def checker(info: Info) -> bool:
        if not hasattr(info, "context") or info.context is None:
            return False
        roles = info.context.get("roles", [])
        if roles is None:
            return False
        return all(role in roles for role in required_roles)

    return checker
