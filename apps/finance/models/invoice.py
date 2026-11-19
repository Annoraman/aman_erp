# apps/finance/models/invoice.py
from django.db import models

from core.models.currency import Currency

class Invoice(models.Model):

    customer = models.ForeignKey("finance.Customer", on_delete=models.PROTECT)

    company = models.ForeignKey("finance.Company", on_delete=models.CASCADE)

    date = models.DateField()

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    is_posted = models.BooleanField(default=False)

    journal = models.ForeignKey(
        "finance.JournalEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    amount = models.DecimalField(...)
    currency = models.ForeignKey(Currency)

    base_amount = models.DecimalField(...)  # converted to base currency