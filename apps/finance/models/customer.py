# apps/finance/models/customer.py
from django.db import models

class Customer(models.Model):

    name = models.CharField(max_length=255)

    company = models.ForeignKey(
        "core.Company",
        on_delete=models.CASCADE
    )

    receivable_account = models.ForeignKey(
        "finance.Account",
        on_delete=models.PROTECT
    )