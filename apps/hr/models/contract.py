# apps/hr/models/contract.py

from django.db import models
from core.models.base import BaseModel


class Contract(BaseModel):

    ACTIVE = "ACTIVE"
    TERMINATED = "TERMINATED"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (TERMINATED, "Terminated"),
    ]

    employee = models.ForeignKey(
        "Employee",
        related_name="contracts",
        on_delete=models.CASCADE
    )

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    salary = models.DecimalField(max_digits=12, decimal_places=2)

    salary_structure = models.ForeignKey(
        "payroll.SalaryStructure",
        on_delete=models.PROTECT
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)

    def __str__(self):
        return f"{self.employee} - {self.salary}"