# apps/payroll/models/salary_structure.py

from django.db import models


class SalaryStructure(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE)

    def __str__(self):
        return self.name