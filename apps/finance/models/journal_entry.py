# apps/finance/models/journal_entry.py

from django.db import models
from django.core.exceptions import ValidationError
from core.models.base import  CompanyAwareModel
from django.utils import timezone
from django.db.models import Sum


class JournalEntry(CompanyAwareModel):

    date = models.DateField(default=timezone.now)

    description = models.TextField()

    reference = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    fiscal_period = models.ForeignKey(
    "finance.FiscalPeriod",
    related_name="journals",
    on_delete=models.PROTECT
    )

    reversed_entry = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="reversal_entry"
    )

    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.ForeignKey("core.Currency", on_delete=models.PROTECT)

    base_amount = models.DecimalField(max_digits=20, decimal_places=2)  # converted to base currency

    is_reversal = models.BooleanField(default=False)

    is_posted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"JE-{self.id} | {self.date}"

    # --------------------------------------------------
    # 🔒 Protect posted entries (safety net)
    # --------------------------------------------------
    def save(self, *args, **kwargs):

        # 🔒 Prevent editing posted entries
        if self.pk:
            old = JournalEntry.objects.select_for_update().filter(pk=self.pk).first()
            if old and old.is_posted:
                raise ValidationError("Cannot modify posted journal entry")

        # ✅ Auto-assign fiscal period if missing
        if not self.fiscal_period_id and self.company_id:
            from apps.finance.services.period_service import PeriodService
            self.fiscal_period = PeriodService.get_period(self.company, self.date)

        super().save(*args, **kwargs)

    # --------------------------------------------------
    # ⚖️ Accounting Helpers
    # --------------------------------------------------
    def total_debit(self):
        return self.lines.aggregate(total=Sum("debit"))["total"] or 0

    def total_credit(self):
        return self.lines.aggregate(total=Sum("credit"))["total"] or 0

    def is_balanced(self):
        return self.total_debit() == self.total_credit()

    # --------------------------------------------------
    # 🧠 Optional Validation Hook (advanced)
    # --------------------------------------------------
    def clean(self):

        # ⚖️ Balance check
        if self.pk and self.lines.exists():
            if not self.is_balanced():
                raise ValidationError("Journal entry is not balanced")

        # 🔁 Prevent reversing a reversal
        if self.is_reversal and self.reversed_entry and self.reversed_entry.is_reversal:
            raise ValidationError("Cannot reverse a reversal entry")

        if self.reversed_entry and hasattr(self.reversed_entry, "reversal_entry"):
            raise ValidationError("This journal is already reversed")