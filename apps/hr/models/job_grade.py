# apps/hr/models/department.py

from django.db import models
from core.models import CompanyAwareModel


class JobGrade(CompanyAwareModel):
    grade = models.CharField(max_length=255)

    def __str__(self):
        return self.grade