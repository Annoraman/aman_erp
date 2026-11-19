# apps/purchase/models/purchase_order.py

from django.db import models
from django.core.exceptions import ValidationError
from core.models.base import CompanyAwareModel
from apps.purchase.constants import POStatus


class PurchaseOrder(CompanyAwareModel):
    supplier = models.ForeignKey(
        "purchase.Supplier",
        on_delete=models.PROTECT,
        related_name="purchase_orders",
    )

    status = models.CharField(
        max_length=20,
        choices=POStatus.choices,
        default=POStatus.DRAFT,
        db_index=True,
    )

    order_date = models.DateField(db_index=True)
    expected_delivery_date = models.DateField(null=True, blank=True)

    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.PROTECT,
    )

    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=1,
    )

    notes = models.TextField(blank=True)

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    class Meta:
        db_table = "purchase_orders"
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["company", "supplier"]),
        ]
        ordering = ["-id"]

    # -------------------------
    # Validation
    # -------------------------
    def clean(self):
        super().clean()

        if self.supplier and self.supplier.company_id != self.company_id:
            raise ValidationError("Supplier must belong to the same company")

        if self.expected_delivery_date and self.expected_delivery_date < self.order_date:
            raise ValidationError("Expected delivery date cannot be before order date")

        if self.exchange_rate <= 0:
            raise ValidationError("Exchange rate must be greater than zero")

    # -------------------------
    # Domain Behavior (Lightweight)
    # -------------------------
    def approve(self):
        if self.status != POStatus.DRAFT:
            raise ValidationError("Only draft purchase orders can be approved")

        if not self.lines.exists():
            raise ValidationError("Cannot approve purchase order without lines")

        self.status = POStatus.APPROVED

    def cancel(self):
        if self.status == POStatus.CANCELLED:
            return

        if self.status == POStatus.APPROVED:
            raise ValidationError("Cannot cancel an approved purchase order")

        self.status = POStatus.CANCELLED

    def mark_as_done(self):
        if self.status != POStatus.APPROVED:
            raise ValidationError("Only approved purchase orders can be completed")

        self.status = POStatus.DONE

    # -------------------------
    # Helpers
    # -------------------------
    def recalculate_total(self):
        total = sum(line.total_amount for line in self.lines.all())
        self.total_amount = total

    # -------------------------
    def __str__(self):
        return f"PO-{self.id}"