# apps/payroll/models/salary_component.py

from django.db import models

from .salary_structure import SalaryStructure


class SalaryComponent(models.Model):

    ALLOWANCE = "ALLOWANCE"
    DEDUCTION = "DEDUCTION"

    TYPE_CHOICES = [
        (ALLOWANCE, "Allowance"),
        (DEDUCTION, "Deduction"),
    ]

    FIXED = "FIXED"
    PERCENTAGE = "PERCENTAGE"

    CALCULATION_TYPE_CHOICES = [
        (FIXED, "Fixed"),
        (PERCENTAGE, "Percentage"),
    ]

    name = models.CharField(max_length=255)
    component_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    calculation_type = models.CharField(max_length=20, choices=CALCULATION_TYPE_CHOICES)

    value = models.DecimalField(max_digits=10, decimal_places=2)

    # percentage based on what?
    based_on_basic = models.BooleanField(default=True)

    salary_structure = models.ForeignKey(
        SalaryStructure,
        related_name="components",
        on_delete=models.CASCADE
    )

    account = models.ForeignKey(
        "finance.Account",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    def __str__(self):
        return self.name