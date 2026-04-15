# from apps.accounts.models import Permission
from apps.accounts.models.permission import Permission

class PermissionSelector:

    @staticmethod
    def get_user_permissions(user, branch=None):

        queryset = Permission.objects.filter(
            permission_roles__role__role_users__user_id=user.id,
            is_active=True
        )

        if branch:
            queryset = queryset.filter(
                permission_roles__role__role_users__branch=branch
            )

        return queryset.distinct()