from django.db import transaction

from apps.accounts.models import RolePermission


class RolePermissionService:

    @staticmethod
    @transaction.atomic
    def assign_permissions(role_id, permission_ids):

        # remove existing permissions
        RolePermission.objects.filter(role_id=role_id).delete()

        role_permissions = [
            RolePermission(
                role_id=role_id,
                permission_id=pid
            )
            for pid in permission_ids
        ]

        RolePermission.objects.bulk_create(role_permissions)

    @staticmethod
    @transaction.atomic
    def add_permission(role_id, permission_id):

        RolePermission.objects.get_or_create(
            role_id=role_id,
            permission_id=permission_id
        )

    @staticmethod
    @transaction.atomic
    def remove_permission(role_id, permission_id):

        RolePermission.objects.filter(
            role_id=role_id,
            permission_id=permission_id
        ).delete()