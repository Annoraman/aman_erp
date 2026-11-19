# apps/payroll/models/salary_component.py

from django.db import models
from apps.hr.models.grade_step import GradeStep
from apps.hr.models.job_grade import JobGrade
from .salary_component import SalaryComponent
from core.models.base import CompanyAwareModel

class SalaryScale(CompanyAwareModel):
    
    grade_step = models.ForeignKey(
        GradeStep, 
        verbose_name=("step"), 
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    
    job_grade = models.ForeignKey(
        JobGrade,        
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )

    code = models.CharField(max_length=50, help_text="Example: BASIC, HRA, TAX")

    component = models.ForeignKey(
        SalaryComponent,        
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )

    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.code} - {self.name}"