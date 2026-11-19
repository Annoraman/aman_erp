# apps/purchase/models/supplier_invoice_line.py

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from core.models.base import CompanyAwareModel


class SupplierInvoiceLine(CompanyAwareModel):
    invoice = models.ForeignKey(
        "purchase.SupplierInvoice",
        on_delete=models.CASCADE,
        related_name="lines",
    )

    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
    )

    po_line = models.ForeignKey(
        "purchase.PurchaseOrderLine",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="invoice_lines",
    )

    grn_line = models.ForeignKey(
        "purchase.GoodsReceiptLine",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="invoice_lines",
    )

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

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    class Meta:
        db_table = "supplier_invoice_lines"
        indexes = [
            models.Index(fields=["invoice", "product"]),
        ]

    # -------------------------
    # Validation
    # -------------------------
    def clean(self):
        super().clean()

        if self.invoice and self.invoice.company_id != self.company_id:
            raise ValidationError("Company mismatch with invoice")

        if self.po_line:
            if self.po_line.company_id != self.company_id:
                raise ValidationError("PO line company mismatch")

            if self.product_id != self.po_line.product_id:
                raise ValidationError("Product mismatch with PO line")

        if self.grn_line:
            if self.grn_line.company_id != self.company_id:
                raise ValidationError("GRN line company mismatch")

            if self.product_id != self.grn_line.product_id:
                raise ValidationError("Product mismatch with GRN line")

        if self.po_line and self.grn_line:
            if self.po_line_id != self.grn_line.po_line_id:
                raise ValidationError("PO line mismatch between GRN and invoice line")

    # -------------------------
    # Domain Behavior
    # -------------------------
    def calculate_total(self):
        self.total_amount = self.quantity * self.unit_price

    # -------------------------
    def __str__(self):
        return f"{self.product} - {self.quantity}"