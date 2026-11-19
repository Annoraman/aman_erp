# apps/payroll/models/payslip_adjustment.py

from django.db import models
from core.models.base import BaseModel


class PayslipAdjustment(BaseModel):

    original_payslip = models.ForeignKey(
        "payroll.Payslip",
        on_delete=models.CASCADE,
        related_name="adjustments"
    )

    payroll_run = models.ForeignKey(
        "payroll.PayrollRun",
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    reason = models.TextField()

    is_processed = models.BooleanField(default=False)