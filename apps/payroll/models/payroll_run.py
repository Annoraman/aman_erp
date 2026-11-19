# apps/payroll/models/payroll_run.py
from django.db import models
from core.models import CompanyAwareModel
from .payroll_period import PayrollPeriod

class PayrollRun(CompanyAwareModel):

    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    POSTED = "POSTED"

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (REVIEW, "Review"),
        (APPROVED, "Approved"), 
        (POSTED, "Posted"),
    ]

    period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE)
    failure_reason = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=DRAFT
    )

    generated_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=False, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["period"], 
                name="uq_payroll_run_period"
                )
        ]
    # 🔐 control fields
    # approved_by = models.ForeignKey(
    #     "accounts.User",
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL
    # )

    # approved_at = models.DateTimeField(null=True, blank=True)

    # posted_at = models.DateTimeField(null=True, blank=True)