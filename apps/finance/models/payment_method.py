# apps/finance/models/payment_method.py

from django.db import models


class PaymentMethod(models.Model):

    METHOD_TYPES = [
        ("CASH", "Cash"),
        ("BANK", "Bank"),
    ]

    name = models.CharField(max_length=100)

    type = models.CharField(max_length=10, choices=METHOD_TYPES)

    account = models.ForeignKey(
        "finance.Account",
        on_delete=models.PROTECT
    )

    company = models.ForeignKey(
        "core.Company",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.name} ({self.type})"