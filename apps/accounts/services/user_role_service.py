from django.db import transaction

from apps.accounts.models import UserRole


class UserRoleService:

    @staticmethod
    @transaction.atomic
    def assign_roles(user_id, role_ids):

        # remove existing roles
        UserRole.objects.filter(user_id=user_id).delete()

        user_roles = [
            UserRole(
                user_id=user_id,
                role_id=role_id
            )
            for role_id in role_ids
        ]

        UserRole.objects.bulk_create(user_roles)

    @staticmethod
    @transaction.atomic
    def add_role(user_id, role_id):

        UserRole.objects.get_or_create(
            user_id=user_id,
            role_id=role_id
        )

    @staticmethod
    @transaction.atomic
    def remove_role(user_id, role_id):

        UserRole.objects.filter(
            user_id=user_id,
            role_id=role_id
        ).delete()