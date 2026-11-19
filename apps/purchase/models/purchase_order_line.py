# apps/purchase/models/purchase_order_line.py

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from core.models.base import CompanyAwareModel


class PurchaseOrderLine(CompanyAwareModel):
    purchase_order = models.ForeignKey(
        "purchase.PurchaseOrder",
        on_delete=models.CASCADE,
        related_name="lines",
    )

    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
    )

    description = models.CharField(max_length=255, blank=True)

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    tax = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    received_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    invoiced_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    class Meta:
        db_table = "purchase_order_lines"
        indexes = [
            models.Index(fields=["purchase_order", "product"]),
        ]

    # -------------------------
    # Validation
    # -------------------------
    def clean(self):
        super().clean()

        if self.purchase_order and self.purchase_order.company_id != self.company_id:
            raise ValidationError("Company mismatch with purchase order")

        if self.discount < 0 or self.discount > 100:
            raise ValidationError("Discount must be between 0 and 100")

        if self.tax < 0 or self.tax > 100:
            raise ValidationError("Tax must be between 0 and 100")

        if self.received_qty > self.quantity:
            raise ValidationError("Received quantity cannot exceed ordered quantity")

        if self.invoiced_qty > self.quantity:
            raise ValidationError("Invoiced quantity cannot exceed ordered quantity")

    # -------------------------
    # Domain Behavior
    # -------------------------
    def calculate_total(self):
        base = self.quantity * self.unit_price
        discount_amount = base * (self.discount / 100)
        taxable = base - discount_amount
        tax_amount = taxable * (self.tax / 100)
        self.total_amount = taxable + tax_amount

    def receive(self, qty):
        if qty <= 0:
            raise ValidationError("Received quantity must be positive")

        if self.received_qty + qty > self.quantity:
            raise ValidationError("Cannot receive more than ordered quantity")

        self.received_qty += qty

    def invoice(self, qty):
        if qty <= 0:
            raise ValidationError("Invoiced quantity must be positive")

        if self.invoiced_qty + qty > self.quantity:
            raise ValidationError("Cannot invoice more than ordered quantity")

        self.invoiced_qty += qty

    # -------------------------
    def __str__(self):
        return f"{self.product} - {self.quantity}"