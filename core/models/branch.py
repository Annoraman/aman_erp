from django.db import models
from core.models.base import BaseModel, AuditModel
from core.models.company import Company


class Branch(BaseModel, AuditModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="branches"
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)

    address = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_branch_code_per_company"
            )
        ]

        indexes = [
            models.Index(fields=["company", "code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.company.name})"