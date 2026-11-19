# apps/payroll/models/salary_component.py

from django.db import models
from core.models.base import CompanyAwareModel

class SalaryComponent(CompanyAwareModel):

    class Type(models.TextChoices):
        EARNING = "EARNING"
        DEDUCTION = "DEDUCTION"

    # class CalcType(models.TextChoices):
    #     FIXED = "FIXED"
    #     PERCENTAGE = "PERCENTAGE"
    #     CALCULATION = "CALCULATION"

    name = models.CharField(max_length=255)

    code = models.CharField(max_length=50, help_text="Example: BASIC, HRA, TAX")

    component_type = models.CharField(max_length=20, choices=Type.choices)

    # calculation_type = models.CharField(max_length=20, choices=CalcType.choices, default=CalcType.FIXED)

    is_taxable = models.BooleanField(default=False)
    is_pensionable = models.BooleanField(default=False)
    is_insurable = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    account = models.ForeignKey(
        "finance.Account",
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )

    class Meta:
        unique_together = ("company", "code")
        indexes = [
            models.Index(fields=["company", "component_type", "is_active"]),
            models.Index(fields=["company", "is_active"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"