from django.db import models
from core.models.base import BaseModel
from django.core.exceptions import ValidationError


class UOMCategory(BaseModel):
    name = models.CharField(max_length=100)

    base_uom = models.ForeignKey(
        "core.UOM",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="base_for_categories"
    )

    def clean(self):
        if self.base_uom:

            # 1. must be marked as base
            if not self.base_uom.is_base:
                raise ValidationError("Base UOM must have is_base=True")

            # 2. must belong to same category
            if self.base_uom.category_id != self.id:
                raise ValidationError("Base UOM must belong to same category")

    def save(self, *args, **kwargs):
        self.full_clean()  # enforce validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name