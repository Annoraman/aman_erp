# apps/finance/models/cost_center.py
from django.db import models
from apps.finance.models.journal_line import JournalLine
from core.models.base import CompanyAwareModel


class CostCenter(CompanyAwareModel):

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children"   # ✅ FIX
    )

    def __str__(self):
        return f"{self.code} - {self.name}"