# apps/purchase/models/goods_receipt.py

from django.db import models
from django.core.exceptions import ValidationError
from core.models.base import CompanyAwareModel
from apps.purchase.constants import GRNStatus


class GoodsReceipt(CompanyAwareModel):
    purchase_order = models.ForeignKey(
        "purchase.PurchaseOrder",
        on_delete=models.PROTECT,
        related_name="goods_receipts",
    )

    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.PROTECT,
    )

    received_date = models.DateTimeField(db_index=True)

    status = models.CharField(
        max_length=20,
        choices=GRNStatus.choices,
        default=GRNStatus.DRAFT,
        db_index=True,
    )

    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.PROTECT,
    )

    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=1,
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    base_total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    class Meta:
        db_table = "goods_receipts"
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["company", "purchase_order"]),
        ]
        ordering = ["-id"]

    # -------------------------
    # Validation
    # -------------------------
    def clean(self):
        super().clean()

        if self.purchase_order and self.purchase_order.company_id != self.company_id:
            raise ValidationError("Purchase order company mismatch")

        if self.exchange_rate <= 0:
            raise ValidationError("Exchange rate must be greater than zero")

    # -------------------------
    # Domain Behavior
    # -------------------------
    def post(self):
        if self.status != GRNStatus.DRAFT:
            raise ValidationError("Only draft goods receipts can be posted")

        if not self.lines.exists():
            raise ValidationError("Cannot post goods receipt without lines")

        self.status = GRNStatus.POSTED

    def cancel(self):
        if self.status == GRNStatus.CANCELLED:
            return

        if self.status == GRNStatus.POSTED:
            raise ValidationError("Cannot cancel a posted goods receipt")

        self.status = GRNStatus.CANCELLED

    # -------------------------
    # Helpers
    # -------------------------
    def recalculate_totals(self):
        total = sum(line.total_amount for line in self.lines.all())
        self.total_amount = total
        self.base_total_amount = total * self.exchange_rate

    # -------------------------
    def __str__(self):
        return f"GRN-{self.id}"