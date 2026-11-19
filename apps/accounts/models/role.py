# accounts/models/role.py

from django.db import models
from core.models import CompanyAwareModel


class Role(CompanyAwareModel):

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    is_system = models.BooleanField(default=False)

    class Meta:
        db_table = "accounts_role"

        ordering = ["name"]

        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_role_code_per_company"
            )
        ]

        indexes = [
            models.Index(fields=["company", "code"]),
            models.Index(fields=["company"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.company.name})"