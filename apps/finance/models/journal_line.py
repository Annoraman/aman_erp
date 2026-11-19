
from django.db import models
from core.models import BaseModel
from core.models.currency import Currency
from .journal_entry import JournalEntry
from django.core.exceptions import ValidationError


class JournalLine(BaseModel):

    journal = models.ForeignKey(
        JournalEntry,
        related_name="lines",
        on_delete=models.CASCADE
    )

    account = models.ForeignKey(
        "finance.Account",
        on_delete=models.PROTECT
    )

    debit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    credit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    cost_center = models.ForeignKey("finance.CostCenter", null=True, blank=True, on_delete=models.SET_NULL)

    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.ForeignKey("core.Currency", on_delete=models.PROTECT)

    base_amount = models.DecimalField(max_digits=20, decimal_places=2)  # converted to base currency

    def __str__(self):
        return f"{self.account} | D:{self.debit} C:{self.credit}"

    # inside JournalLine

    def save(self, *args, **kwargs):

        if self.journal.is_posted:
            raise ValidationError("Cannot modify posted journal entry")

        self.full_clean()

        super().save(*args, **kwargs)

    def clean(self):

        # ❌ Prevent both debit & credit
        if self.debit > 0 and self.credit > 0:
            raise ValidationError("Line cannot have both debit and credit")

        # ❌ Prevent empty line
        if self.debit == 0 and self.credit == 0:
            raise ValidationError("Line must have debit or credit")

        # ❌ Company validation
        if self.account.company_id != self.journal.company_id:
            raise ValidationError("Account must belong to same company as journal")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(debit__gt=0, credit=0) |
                    models.Q(credit__gt=0, debit=0)
                ),
                name="journal_line_debit_credit_exclusive"
            )
        ]
