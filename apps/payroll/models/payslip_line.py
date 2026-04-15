# apps/payroll/models/payslip_line.py

from django.db import models


class PayslipLine(models.Model):

    ALLOWANCE = "ALLOWANCE"
    DEDUCTION = "DEDUCTION"

    TYPE_CHOICES = [
        (ALLOWANCE, "Allowance"),
        (DEDUCTION, "Deduction"),
    ]

    payslip = models.ForeignKey(
        "payroll.Payslip",
        related_name="lines",
        on_delete=models.CASCADE
    )

    account = models.ForeignKey(
    "finance.Account",
    null=True,
    blank=True,
    on_delete=models.PROTECT
    )
    component_name = models.CharField(max_length=255)
    component_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.component_name} - {self.amount}"