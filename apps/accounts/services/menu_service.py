#accounts/services/menu_service.py

from apps.accounts.services.permission_service import PermissionService
from apps.accounts.rbac.rbac_blueprint import RBAC_BLUEPRINT


class MenuService:

    @staticmethod
    def get_user_menu(user):

        user_permissions = PermissionService.get_user_permissions(user)

        menu = {}

        for module, permissions in RBAC_BLUEPRINT.items():

            allowed = [
                perm for perm in permissions
                if perm in user_permissions
            ]

            if allowed:
                menu[module] = allowed

        return menu
