# apps/purchase/models/goods_receipt_line.py

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from core.models.base import CompanyAwareModel


class GoodsReceiptLine(CompanyAwareModel):
    goods_receipt = models.ForeignKey(
        "purchase.GoodsReceipt",
        on_delete=models.CASCADE,
        related_name="lines",
    )

    purchase_order_line = models.ForeignKey(
        "purchase.PurchaseOrderLine",
        on_delete=models.PROTECT,
        related_name="grn_lines",
    )

    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
    )

    received_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    invoiced_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    class Meta:
        db_table = "goods_receipt_lines"
        indexes = [
            models.Index(fields=["goods_receipt", "product"]),
        ]

    # -------------------------
    # Validation
    # -------------------------
    def clean(self):
        super().clean()

        if self.goods_receipt and self.goods_receipt.company_id != self.company_id:
            raise ValidationError("Company mismatch with goods receipt")

        if self.purchase_order_line:
            if self.purchase_order_line.company_id != self.company_id:
                raise ValidationError("PO line company mismatch")

            if self.product_id != self.purchase_order_line.product_id:
                raise ValidationError("Product mismatch with PO line")

        if self.received_quantity < 0:
            raise ValidationError("Received quantity cannot be negative")

        if self.invoiced_quantity < 0:
            raise ValidationError("Invoiced quantity cannot be negative")

        if self.invoiced_quantity > self.received_quantity:
            raise ValidationError("Invoiced quantity cannot exceed received quantity")

    # -------------------------
    # Domain Behavior
    # -------------------------
    def calculate_total(self):
        unit_price = self.purchase_order_line.unit_price
        self.total_amount = self.received_quantity * unit_price

    def invoice(self, qty):
        if qty <= 0:
            raise ValidationError("Invoice quantity must be positive")

        if self.invoiced_quantity + qty > self.received_quantity:
            raise ValidationError("Cannot invoice more than received quantity")

        self.invoiced_quantity += qty

    # -------------------------
    def __str__(self):
        return f"{self.product} - {self.received_quantity}"