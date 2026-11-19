from django.db import models
from .base import BaseModel


class ExchangeRate(BaseModel):
    from_currency = models.ForeignKey("core.Currency", on_delete=models.PROTECT, related_name="from_rates")
    to_currency = models.ForeignKey("core.Currency", on_delete=models.PROTECT, related_name="to_rates")

    rate = models.DecimalField(max_digits=20, decimal_places=10)

    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "exchange_rates"
        unique_together = ("from_currency", "to_currency", "valid_from")
        indexes = [
            models.Index(fields=["valid_from"]),
            models.Index(fields=["from_currency", "to_currency"]),
        ]

    def __str__(self):
        return f"{self.from_currency} -> {self.to_currency}"