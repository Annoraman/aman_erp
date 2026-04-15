# apps/finance/models/bank_statement.py
from django.db import models


class BankStatement(models.Model):

    company = models.ForeignKey(
        "core.Company",
        on_delete=models.CASCADE
    )

    payment_method = models.ForeignKey(
        "finance.PaymentMethod",
        on_delete=models.PROTECT
    )

    date = models.DateField()

    balance = models.DecimalField(max_digits=12, decimal_places=2)