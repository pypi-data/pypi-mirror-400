import logging
from typing import Dict, Optional

from strawberry.types import Info

from .permission_helpers import (
    PermissionChecker,
    has_all_roles,
    has_any_role,
    has_role,
    is_admin,
    is_authenticated,
)

logger = logging.getLogger(__name__)


class PermissionDenied(Exception):
    """
    Raised when a user lacks permission to perform an operation.

    This exception should be caught and converted to a GraphQL error
    in the resolver layer.
    """

    def __init__(self, operation: str, message: Optional[str] = None):
        self.operation = operation
        self.message = (
            message or f"Permission denied for operation: {operation}"
        )
        super().__init__(self.message)


class PermissionManager:
    """
    Manages permissions for CRUD operations.

    Each operation can have a custom permission checker function that receives
    the GraphQL Info context and returns True if allowed, False otherwise.
    """

    def __init__(
        self, permissions: Optional[Dict[str, PermissionChecker]] = None
    ):
        """
        Initialize permission manager.

        Args:
            permissions: Dict mapping operation names to checker functions
                        Operations: "create", "update", "delete", "list"
        """
        self.permissions: Dict[str, PermissionChecker] = permissions or {}

    def check(self, operation: str, info: Info) -> bool:
        """
        Check if operation is permitted.

        Args:
            operation: Name of the operation
                ("create", "update", "delete", "list")
            info: Strawberry Info context containing user, db, etc.

        Returns:
            True if permitted, False otherwise
        """
        if (
            info is None
            or not hasattr(info, "context")
            or info.context is None
        ):
            logger.debug(
                f"Permission check failed: no context for operation "
                f"'{operation}'"
            )
            return False

        if not self.permissions:
            # No permissions configured means all operations are allowed
            return True

        checker = self.permissions.get(operation)

        # No checker means operation is allowed by default
        if checker is None:
            return True

        try:
            result = checker(info)
            if not result:
                logger.debug(
                    f"Permission denied for operation '{operation}' by checker"
                )
            return result
        except Exception as e:
            logger.error(
                f"Error in permission checker for operation "
                f"'{operation}': {e}",
                exc_info=True,
            )
            # Fail closed: deny permission on error
            return False

    def ensure_permission(self, operation: str, info: Info) -> None:
        """
        Ensure permission or raise PermissionDenied.

        Args:
            operation: Name of the operation
            info: Strawberry Info context

        Raises:
            PermissionDenied: If permission check fails
        """
        if not self.check(operation, info):
            logger.warning(
                f"Permission denied for operation '{operation}' "
                f"by user '{info.context.get('user', 'unknown')}'"
            )
            raise PermissionDenied(operation)


# Permission helper functions are exported for backward compatibility
__all__ = [
    "PermissionDenied",
    "PermissionManager",
    "PermissionChecker",
    "has_all_roles",
    "has_any_role",
    "has_role",
    "is_admin",
    "is_authenticated",
]
