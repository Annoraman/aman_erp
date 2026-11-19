# apps/hr/models/leave_type.py

from django.db import models
from core.models.base import CompanyAwareModel


class LeaveType(CompanyAwareModel):

    name = models.CharField(max_length=100)

    is_paid = models.BooleanField(default=True)

    deduct_from_salary = models.BooleanField(default=False)

    max_days_per_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name