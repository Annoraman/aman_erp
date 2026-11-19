# apps/payroll/models/salary_rule.py

from django.db import models
from core.models.base import CompanyAwareModel

class SalaryRule(CompanyAwareModel):

    name = models.CharField(max_length=255)

    salary_structure = models.ForeignKey(
        "payroll.SalaryStructure",
        on_delete=models.CASCADE
    )

    component = models.ForeignKey(
        "payroll.SalaryComponent",
        on_delete=models.PROTECT
    )

    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name    