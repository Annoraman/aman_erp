# apps/payroll/models/payslip.py

from django.db import models
from core.models.base import CompanyAwareModel
from django.core.exceptions import ValidationError
# from config import settings

class Payslip(CompanyAwareModel):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        CONFIRMED = "CONFIRMED", "Confirmed"
        APPROVED = "APPROVED", "Approved"
        POSTED = "POSTED", "Posted"

    employee = models.ForeignKey("hr.Employee", on_delete=models.PROTECT)

    contract = models.ForeignKey(
        "hr.Contract",
        on_delete=models.PROTECT,
        related_name="payslip_set"
    )

    payroll_run = models.ForeignKey(
        "payroll.PayrollRun",
        on_delete=models.PROTECT,
        related_name="payslips"
    )

    # approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    # approved_at = models.DateTimeField(null=True, blank=True)

    # posted_at = models.DateTimeField(null=True, blank=True)

    period = models.ForeignKey("payroll.PayrollPeriod", verbose_name="payslip_period", on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT )
    debug = models.JSONField(default=dict, blank=True, null=True)
    
    # ✅ Summary fields (computed)
    
    taxable_gross = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    insurable_gross = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    pensionable_gross = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    gross_salary = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        unique_together = ("employee", "payroll_run")

    def __str__(self):
        return f"{self.employee} - {self.period_start}"

    def save(self, *args, **kwargs):
        if self.pk:
            old = Payslip.objects.get(pk=self.pk)
            if old.status == "POSTED":
                raise ValidationError("Cannot modify posted payslip")
        super().save(*args, **kwargs)