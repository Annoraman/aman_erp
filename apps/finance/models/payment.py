from django.db import models
from core.models.base import CompanyAwareModel
from core.models.currency import Currency


class Payment(CompanyAwareModel):

    PAYMENT_TYPES = [
        ("PAY", "Pay Supplier"),
        ("RECEIVE", "Receive Customer"),
    ]

    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPES)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    date = models.DateField()

    method = models.ForeignKey("finance.PaymentMethod", on_delete=models.PROTECT)

    supplier = models.ForeignKey(
        "purchases.Supplier",
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

    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)

    base_amount = models.DecimalField(max_digits=12, decimal_places=2)

