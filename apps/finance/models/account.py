# apps/finance/models/account.py

from django.db import models
from django.core.exceptions import ValidationError
from core.models.base import CompanyAwareModel

class Account(CompanyAwareModel):

    ACCOUNT_TYPES = [
        ("ASSET", "Asset"),
        ("LIABILITY", "Liability"),
        ("EQUITY", "Equity"),
        ("INCOME", "Income"),
        ("EXPENSE", "Expense"),
    ]

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)

    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        if self.parent and self.parent.company_id != self.company_id:
            raise ValidationError("Parent account must belong to same company")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_account_code_per_company"
            )
        ]
        indexes = [
            models.Index(fields=["company", "code"]),
        ]