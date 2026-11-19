# apps/purchase/models/stock_movement.py

from django.db import models
from django.core.exceptions import ValidationError
from core.models.base import CompanyAwareModel


class StockMovement(CompanyAwareModel):

    class MovementType(models.TextChoices):
        IN = "IN", "Stock In"
        OUT = "OUT", "Stock Out"
        TRANSFER = "TRANSFER", "Transfer"

    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT
    )

    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.PROTECT
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices
    )

    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=3
    )

    reference = models.CharField(
        max_length=100,
        blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["company", "product", "warehouse"]),
            models.Index(fields=["created_at"]),
        ]

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than 0")

        if self.movement_type == self.MovementType.TRANSFER and not self.warehouse:
            raise ValidationError("Transfer must have warehouse defined")