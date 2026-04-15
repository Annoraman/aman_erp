# apps/payroll/models/payroll_run.py
from django.db import models
from core.models import BaseModel
from .payroll_period import PayrollPeriod

class PayrollRun(models.Model):
    
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

    period = models.ForeignKey("payroll.PayrollPeriod", on_delete=models.CASCADE)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=DRAFT
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔐 control fields
    approved_by = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    posted_at = models.DateTimeField(null=True, blank=True)