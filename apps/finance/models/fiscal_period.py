# apps/finance/models/fiscal_period.py
from django.db.models import Q, F
from django.db import models
from django.core.exceptions import ValidationError

class FiscalPeriod(models.Model):
    
    fiscal_year = models.ForeignKey(
        "finance.FiscalYear",
        on_delete=models.PROTECT,
        related_name="periods"
    )

    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def company(self):
        return self.fiscal_year.company

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Period start date must be before end date")
            if self.start_date > self.end_date:
                raise ValidationError("Invalid period dates")

        overlapping = FiscalPeriod.objects.filter(
            fiscal_year=self.fiscal_year,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        )

        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("Fiscal period overlaps with another period")
        
        if self.fiscal_year.is_closed:
            raise ValidationError("Cannot add period to closed fiscal year")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["fiscal_year", "name"],
                name="unique_period_name_per_year"
            )
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(start_date__lte=F("end_date")),
                name="period_start_before_end"
            ),
        ]
        indexes = [
            models.Index(fields=["fiscal_year", "start_date", "end_date"]),
        ]
