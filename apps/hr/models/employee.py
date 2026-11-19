# apps/hr/models/employee.py

from django.db import models
from django.core.exceptions import ValidationError
from core.models.base import CompanyAwareModel
from .grade_step import GradeStep
from .job_grade import JobGrade


class Employee(CompanyAwareModel):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    employee_code = models.CharField(max_length=50)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    hire_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    department = models.ForeignKey(
        "hr.Department",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="employees"
    )

    job = models.ForeignKey(
        "hr.Job",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="employees"
    )

    branch = models.ForeignKey(
        "core.branch",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="employees"
    )

    manager = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="subordinates"
    )

    job_grade = models.ForeignKey(JobGrade, verbose_name=("grade"), on_delete=models.CASCADE)
    
    grade_step = models.ForeignKey(GradeStep, verbose_name=("step"), on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "employee_code"],
                name="unique_employee_code_per_company"
            )
        ]
        indexes = [
            models.Index(fields=["company", "employee_code"]),
            models.Index(fields=["status"]),
            models.Index(fields=["department"]),
        ]

    def clean(self):
        # ❗ Prevent self as manager
        if self.manager and self.manager == self:
            raise ValidationError("Employee cannot be their own manager.")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.employee_code} - {self.full_name}"