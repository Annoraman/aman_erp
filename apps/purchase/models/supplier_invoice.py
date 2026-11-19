# apps/purchase/models/supplier_invoice.py

from django.db import models
from django.core.exceptions import ValidationError
from core.models.base import CompanyAwareModel
from apps.purchase.constants import InvoiceStatus


class SupplierInvoice(CompanyAwareModel):
    supplier = models.ForeignKey(
        "purchase.Supplier",
        on_delete=models.PROTECT,
    )

    goods_receipt = models.ForeignKey(
        "purchase.GoodsReceipt",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="invoices",
    )

    journal_entry = models.ForeignKey(
        "finance.JournalEntry",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    invoice_date = models.DateField(db_index=True)

    paid_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
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
        db_table = "supplier_invoices"
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
            raise ValidationError("Supplier must belong to same company")

        if self.goods_receipt:
            if self.goods_receipt.company_id != self.company_id:
                raise ValidationError("Goods receipt company mismatch")

            if self.goods_receipt.purchase_order.supplier_id != self.supplier_id:
                raise ValidationError("Supplier mismatch with goods receipt")

        if self.exchange_rate <= 0:
            raise ValidationError("Exchange rate must be greater than zero")

        if self.paid_amount < 0:
            raise ValidationError("Paid amount cannot be negative")

        if self.paid_amount > self.total_amount:
            raise ValidationError("Paid amount cannot exceed total amount")

    # -------------------------
    # Domain Behavior
    # -------------------------
    def mark_matched(self):
        if self.status != InvoiceStatus.DRAFT:
            raise ValidationError("Only draft invoices can be matched")

        self.status = InvoiceStatus.MATCHED

    def post(self):
        if self.status != InvoiceStatus.MATCHED:
            raise ValidationError("Only matched invoices can be posted")

        if not self.journal_entry:
            raise ValidationError("Journal entry is required before posting")

        self.status = InvoiceStatus.POSTED

    def register_payment(self, amount):
        if amount <= 0:
            raise ValidationError("Payment amount must be positive")

        if self.status not in [InvoiceStatus.POSTED, InvoiceStatus.PARTIALLY_PAID]:
            raise ValidationError("Invoice must be posted before payment")

        if self.paid_amount + amount > self.total_amount:
            raise ValidationError("Payment exceeds invoice amount")

        self.paid_amount += amount

        if self.paid_amount == self.total_amount:
            self.status = InvoiceStatus.PAID
        else:
            self.status = InvoiceStatus.PARTIALLY_PAID

    # -------------------------
    # Helpers
    # -------------------------
    def recalculate_totals(self):
        total = sum(line.total_amount for line in self.lines.all())
        self.total_amount = total
        self.base_total_amount = total * self.exchange_rate

    # -------------------------
    def __str__(self):
        return f"INV-{self.id}"