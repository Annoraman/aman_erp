# apps/finance/models/bank_statement_line.py

from django.db import models

class BankStatementLine(models.Model):

    statement = models.ForeignKey(
        "finance.BankStatement",
        related_name="lines",
        on_delete=models.CASCADE
    )

    date = models.DateField()

    description = models.CharField(max_length=255)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    is_matched = models.BooleanField(default=False)

    matched_payment = models.ForeignKey(
        "finance.Payment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )