# accounts/models/user_roles.py

from django.db import models
from django.conf import settings
from core.models.base import BaseModel, AuditModel
from core.models.branch import Branch
from .role import Role


class UserRole(BaseModel, AuditModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles"
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_users"
    )

    branch = models.ForeignKey(
        Branch,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="branch_user_roles"
    )

    class Meta:
        db_table = "accounts_user_role"

        ordering = ["user"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "role", "branch"],
                name="unique_user_role_per_branch"
            )
        ]

        indexes = [
            models.Index(fields=["user", "role"]),
            models.Index(fields=["user", "branch"]),
            models.Index(fields=["role"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):

        if self.branch:
            return f"{self.user.email} → {self.role.name} ({self.branch.name})"

        return f"{self.user.email} → {self.role.name}"