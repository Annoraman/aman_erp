# apps/hr/models/contract.py

from django.db import models
from django.core.exceptions import ValidationError
from core.models.base import CompanyAwareModel

 
class Contract(CompanyAwareModel):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        TERMINATED = "TERMINATED", "Terminated"
        SUSPENDED = "SUSPENDED", "suspended"
        DRAFT ="DRAFT", "draft"

    employee = models.ForeignKey(
        "hr.Employee",
        related_name="contracts",
        on_delete=models.CASCADE
    )

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    # 🔥 renamed for clarity
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)

    salary_structure = models.ForeignKey(
        "payroll.SalaryStructure",
        on_delete=models.PROTECT,
        related_name="contracts"
    )

    # department = models.ForeignKey("hr.Department", on_delete=models.PROTECT)
    job = models.ForeignKey("hr.Job", on_delete=models.PROTECT)

    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    class Meta:
        indexes = [
            models.Index(fields=["employee", "status"]),
            models.Index(fields=["start_date", "end_date"]),
        ]

    def clean(self):
        # ❗ Date validation
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")

        # ❗ Only one ACTIVE contract per employee
        if self.status == self.Status.ACTIVE:
            qs = Contract.objects.filter(
                employee=self.employee,
                status=self.Status.ACTIVE
            ).exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError("Employee already has an active contract.")

    def __str__(self):
        return f"{self.employee} - {self.basic_salary}"