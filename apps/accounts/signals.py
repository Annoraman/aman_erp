from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.accounts.models import UserRole, RolePermission
from apps.accounts.cache.permission_cache import PermissionCache


# ---------------------------------------------------------
# Clear cache when user roles change
# ---------------------------------------------------------

@receiver(post_save, sender=UserRole)
@receiver(post_delete, sender=UserRole)
def clear_userrole_cache(sender, instance, **kwargs):

    user = instance.user

    if user:
        PermissionCache.clear_permissions(user)


# ---------------------------------------------------------
# Clear cache when role permissions change
# ---------------------------------------------------------

@receiver(post_save, sender=RolePermission)
@receiver(post_delete, sender=RolePermission)
def clear_rolepermission_cache(sender, instance, **kwargs):

    role = instance.role

    if not role:
        return

    # Get users that have this role
    user_roles = UserRole.objects.filter(role=role).select_related("user")

    for ur in user_roles:
        PermissionCache.clear_permissions(ur.user)