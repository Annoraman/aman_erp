# accounts/models/permission.py

from django.db import models
from core.models.base import BaseModel, AuditModel
from core.models.branch import Branch
from core.models import CompanyAwareModel


class Permission(CompanyAwareModel):


    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.CASCADE,
        related_name="branch_permissions"
    )

    module = models.ForeignKey(
        "accounts.Module",
        on_delete=models.PROTECT,
        related_name="permissions"
    )

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=100)
    description = models.CharField(max_length=150, null=True)
    is_system = models.BooleanField(default=False)

    class Meta:
        db_table = "accounts_permission"

        ordering = ["module", "code"]

        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_permission_per_company"
            )
        ]

        indexes = [
            models.Index(fields=["company", "code"]),
            models.Index(fields=["module"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.module.code}.{self.code}"