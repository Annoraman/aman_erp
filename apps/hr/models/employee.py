# apps/hr/models/employee.py

from django.db import models
from core.models.base import BaseModel


class Employee(BaseModel):

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive"),
    ]

    employee_code = models.CharField(max_length=50, unique=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    hire_date = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)

    company = models.ForeignKey("core.Company", on_delete=models.CASCADE)

    department = models.ForeignKey(
        "Department",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="employees"
    )

    job = models.ForeignKey(
        "Job",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    manager = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"