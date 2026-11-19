# apps/hr/models/department.py

from django.db import models
from core.models import CompanyAwareModel


class Department(CompanyAwareModel):
    name = models.CharField(max_length=255)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE
    )

    manager = models.ForeignKey(
        "Employee",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managed_departments"
    )

    company = models.ForeignKey("core.Company", on_delete=models.CASCADE)

    def __str__(self):
        return self.name