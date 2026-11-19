from django.db import models
from core.models.base import BaseModel
from django.core.exceptions import ValidationError


class UOM(BaseModel):

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    category = models.ForeignKey(
        "core.UOMCategory",
        on_delete=models.PROTECT,
        related_name="uoms"
    )

    is_base = models.BooleanField(default=False)

    # conversion factor relative to base unit
    ratio_to_base = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        default=1
    )

    class Meta:
        db_table = "uoms"

    def __str__(self):
        return self.code

    def clean(self):
        # Only one base per category
        if self.is_base:
            qs = UOM.objects.filter(
                category=self.category,
                is_base=True
            ).exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError("Only one base UOM allowed per category")

        # base UOM must have factor = 1
        if self.is_base and self.factor != 1:
            raise ValidationError("Base UOM must have factor = 1")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)