# apps/hr/models/department.py

from django.db import models
from core.models import CompanyAwareModel


class GradeStep(CompanyAwareModel):
    
    grade = models.ForeignKey("hr.JobGrade", verbose_name=("Grade"), on_delete=models.CASCADE)
    step = models.CharField(max_length=255)

    def __str__(self):
        return self.step
    