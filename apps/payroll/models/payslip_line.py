# apps/payroll/models/payslip_line.py
from django.db import models
from core.models.base import CompanyAwareModel

class PayslipLine(CompanyAwareModel):
    
    payslip = models.ForeignKey(
        "payroll.Payslip",
        related_name="lines",
        on_delete=models.CASCADE
    )

    component_id = models.IntegerField()

    component_name = models.CharField(max_length=255)
    component_code = models.CharField(max_length=50)
    component_type = models.CharField(max_length=50)
    sequence = models.IntegerField(default=0)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    rule_version_id = models.IntegerField(blank=True, null=True)
    formula_snapshot = models.TextField(blank=True, null=True)
    condition_snapshot = models.TextField(blank=True, null=True)
    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["payslip"]),
            models.Index(fields=["component_code"]),
        ]
        unique_together = ("payslip", "component_code")