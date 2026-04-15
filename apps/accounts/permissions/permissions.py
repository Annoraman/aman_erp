#apps/account/permissions.py
from rest_framework.permissions import BasePermission
from apps.accounts.services.permission_service import PermissionService


class HasPermission(BasePermission):

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        permission_code = getattr(view, "permission_code", None)

        if not permission_code:
            return True  # If not defined, allow

        return PermissionService.has_permission(
            request.user,
            permission_code
        )
