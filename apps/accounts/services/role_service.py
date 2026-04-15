from django.db import transaction

from apps.accounts.models import Role
from apps.accounts.selectors.role_selector import RoleSelector


class RoleService:

    @staticmethod
    @transaction.atomic
    def create_role(name, description=None, created_by=None):

        role = Role.objects.create(
            name=name,
            description=description,
            created_by=created_by
        )

        return role

    @staticmethod
    @transaction.atomic
    def update_role(role_id, name=None, description=None):

        role = RoleSelector.get_role(role_id)

        if not role:
            raise ValueError("Role not found")

        if name is not None:
            role.name = name

        if description is not None:
            role.description = description

        role.save()

        return role

    @staticmethod
    @transaction.atomic
    def delete_role(role_id):

        role = RoleSelector.get_role(role_id)

        if not role:
            raise ValueError("Role not found")

        role.delete()