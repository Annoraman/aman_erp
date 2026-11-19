# apps/hr/models/attendance.py

from django.db import models
from core.models.base import CompanyAwareModel


class Attendance(CompanyAwareModel):

    employee = models.ForeignKey("hr.Employee", on_delete=models.CASCADE)

    date = models.DateField()

    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    worked_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )

    is_absent = models.BooleanField(default=False)
    is_late = models.BooleanField(default=False)

    class Meta:
        unique_together = ("employee", "date")