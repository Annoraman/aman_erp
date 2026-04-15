# apps/payroll/models/payslip.py

from django.db import models

from .payroll_run import PayrollRun
from core.models.base import BaseModel

class Payslip(BaseModel):

    employee = models.ForeignKey("hr.Employee", on_delete=models.CASCADE)
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE)

    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
