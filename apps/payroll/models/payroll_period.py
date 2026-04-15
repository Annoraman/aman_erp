# apps/payroll/models/payroll_period.py

from django.db import models

class PayrollPeriod(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)