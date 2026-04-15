# apps/accounts/cache/permission_cache.py


# apps/accounts/cache/permission_cache.py

from django.core.cache import cache
from apps.accounts.selectors.permission_selector import PermissionSelector


class PermissionCache:

    CACHE_PREFIX = "user_permissions"

    @staticmethod
    def _get_cache_key(user_id, branch_id=None):
        return f"{PermissionCache.CACHE_PREFIX}:{user_id}:{branch_id}"

    @staticmethod
    def load_permissions(user, branch=None):

        branch_id = branch.id if branch else None
        cache_key = PermissionCache._get_cache_key(user.id, branch_id)

        permissions = cache.get(cache_key)

        if permissions is not None:
            return permissions

        # Load from database
        permissions = PermissionSelector.get_user_permissions(
            user=user,
            branch=branch
        )

        # Convert to set of codes
        permission_codes = set(p.code for p in permissions)

        # Save to cache
        cache.set(cache_key, permission_codes, timeout=3600)

        return permission_codes

    @staticmethod
    def clear_user_cache(user_id, branch_id=None):

        cache_key = PermissionCache._get_cache_key(user_id, branch_id)
        cache.delete(cache_key)

    @staticmethod
    def clear_permissions(user, branch=None):
        branch_id = branch.id if branch else None
        cache_key = PermissionCache._get_cache_key(user.id, branch_id)
        cache.delete(cache_key)