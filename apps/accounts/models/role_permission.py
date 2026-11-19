# accounts/models/role_permission.py

from django.db import models
from core.models import CompanyAwareModel
from .role import Role
from .permission import Permission


class RolePermission(CompanyAwareModel):

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions"
    )

    permission = models.ForeignKey(
        Permission,
        on_delete=models.PROTECT,
        related_name="permission_roles"
    )

    class Meta:
        db_table = "accounts_role_permission"

        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="unique_permission_per_role"
            )
        ]

        indexes = [
            models.Index(fields=["role", "permission"]),
            models.Index(fields=["role"]),
            models.Index(fields=["permission"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.role.code} → {self.permission.code}"