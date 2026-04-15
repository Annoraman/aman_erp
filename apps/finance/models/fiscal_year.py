# apps/finance/models/fiscal_year.py

from django.db import models
from django.core.exceptions import ValidationError
from core.models.base import CompanyAwareModel

class FiscalYear(CompanyAwareModel):

    name = models.CharField(max_length=20)  # e.g. 2026
    start_date = models.DateField()
    end_date = models.DateField()

    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company} - {self.name}"

    def clean(self):

        if self.start_date > self.end_date:
            raise ValidationError("Fiscal year start date must be before end date")

        if self.start_date > self.end_date:
            raise ValidationError("Invalid fiscal year dates")

        overlapping = FiscalYear.objects.filter(
            company=self.company,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        )

        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("Fiscal year overlaps with another year")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"],
                name="unique_fiscal_year_per_company"
            )
        ]

        indexes = [
            models.Index(fields=["company", "start_date", "end_date"]),
        ]