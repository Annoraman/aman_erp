# apps/finance/models/payment.py
from django.db import models 

class Payment(models.Model):

    PAYMENT_TYPES = [
        ("PAY", "Pay Vendor"),
        ("RECEIVE", "Receive Customer"),
    ]

    company = models.ForeignKey("core.Company", on_delete=models.CASCADE)

    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    date = models.DateField()

    method = models.ForeignKey("finance.PaymentMethod", on_delete=models.PROTECT)

    vendor = models.ForeignKey(
        "finance.Vendor",
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    customer = models.ForeignKey(
        "finance.Customer",
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    is_posted = models.BooleanField(default=False)

    journal = models.ForeignKey(
        "finance.JournalEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )