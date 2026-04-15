from apps.accounts.cache.permission_cache import PermissionCache
from apps.accounts.selectors.permission_selector import PermissionSelector


class PermissionService:

    INHERIT_MAP = {
        "manage_system": [
            "view_system",
        ],
    }

    @staticmethod
    def get_user_permissions(user):

        if not user.is_authenticated:
            return set()

        cached = PermissionCache.load_permissions(user)

        if cached is not None:
            return cached

        permissions = PermissionSelector.get_user_permissions(user)

        PermissionCache.set_permissions(user, permissions)

        return permissions

    @staticmethod
    def has_permission(user, permission_code, company=None):

        if not user or not user.is_authenticated:
            return False

        if getattr(user, "is_super_admin", False):
            return True

        permissions = PermissionService.get_user_permissions(user)

        has_perm = False

        if permission_code in permissions:
            has_perm = True
        else:
            for parent, children in PermissionService.INHERIT_MAP.items():
                if parent in permissions and permission_code in children:
                    has_perm = True
                    break

        if not has_perm:
            return False

        if company:
            return PermissionService._check_company_access(user, company)

        return True

    @staticmethod
    def has_any_permission(user, permission_codes):

        for code in permission_codes:
            if PermissionService.has_permission(user, code):
                return True

        return False

    @staticmethod
    def has_all_permissions(user, permission_codes):

        for code in permission_codes:
            if not PermissionService.has_permission(user, code):
                return False

        return True

    @staticmethod
    def _check_company_access(user, company):
        """
        Basic company isolation
        """

        # Simple version (recommended for now)
        return getattr(user, "company_id", None) == company.id

        # Future (multi-company users)
        # return company in user.allowed_companies.all()


    @staticmethod
    def clear_user_permissions(user):
        PermissionCache.clear_permissions(user)