
from django.db import models
from core.models.base import BaseModel


class PaymentAllocation(BaseModel):
    payment = models.ForeignKey(
        "finance.Payment",
        on_delete=models.CASCADE,
        related_name="allocations"
    )

    invoice = models.ForeignKey(
        "purchases.SupplierInvoice",
        on_delete=models.PROTECT
    )

    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2)