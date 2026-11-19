# apps/hr/models/leave_request.py

from django.db import models
from config import settings
from core.models.base import CompanyAwareModel


class LeaveRequest(CompanyAwareModel):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    employee = models.ForeignKey(
        "hr.Employee",
        on_delete=models.CASCADE
    )

    leave_type = models.ForeignKey(
        "hr.LeaveType",
        on_delete=models.PROTECT
    )

    start_date = models.DateField()
    end_date = models.DateField()

    reason = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="accepted_leave_requests"
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,        
        related_name="approved_leave_requests"
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.leave_type}"