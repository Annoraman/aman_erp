# apps/finance/models/vendor.py
from django.db import models

class Vendor(models.Model):

    name = models.CharField(max_length=255)

    company = models.ForeignKey(
        "core.Company",
        on_delete=models.CASCADE
    )

    payable_account = models.ForeignKey(
        "finance.Account",
        on_delete=models.PROTECT
    )

    def __str__(self):
        return self.name