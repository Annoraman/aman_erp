from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError

from core.models.base import CompanyAwareModel


class PurchaseConfig(CompanyAwareModel):
    """
    Company-level purchase configuration.
    Controls validation rules for:
    - GRN matching
    - Invoice matching
    - Tolerance rules
    - Accounting integration
    """

    quantity_tolerance_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    price_tolerance_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    strict_mode = models.BooleanField(
        default=True,
        help_text="If enabled, blocks mismatches strictly instead of warnings",
    )

    grni_account = models.ForeignKey(
        "finance.Account",
        on_delete=models.PROTECT,
        help_text="Goods Received Not Invoiced (GRNI) account",
    )

    class Meta:
        db_table = "purchase_config"
        verbose_name = "Purchase Configuration"
        verbose_name_plural = "Purchase Configuration"

    # -------------------------
    # Validation
    # -------------------------
    def clean(self):
        super().clean()

        if self.quantity_tolerance_percent < 0:
            raise ValidationError("Quantity tolerance cannot be negative")

        if self.price_tolerance_percent < 0:
            raise ValidationError("Price tolerance cannot be negative")

        if self.quantity_tolerance_percent > 100:
            raise ValidationError("Quantity tolerance cannot exceed 100%")

        if self.price_tolerance_percent > 100:
            raise ValidationError("Price tolerance cannot exceed 100%")

        if self.grni_account and self.grni_account.company_id != self.company_id:
            raise ValidationError("GRNI account must belong to same company")

    # -------------------------
    # Domain Logic
    # -------------------------
    @staticmethod
    def within_tolerance(value1: Decimal, value2: Decimal, tolerance_percent: Decimal) -> bool:
        """
        Generic ERP tolerance check.
        Used for:
        - quantity matching (GRN vs invoice)
        - price matching
        """

        if value2 == 0:
            return value1 == 0

        diff = abs(value1 - value2)
        percent = (diff / value2) * Decimal("100")

        return percent <= tolerance_percent

    def is_quantity_valid(self, grn_qty: Decimal, invoice_qty: Decimal) -> bool:
        return self.within_tolerance(
            grn_qty,
            invoice_qty,
            self.quantity_tolerance_percent,
        )

    def is_price_valid(self, grn_price: Decimal, invoice_price: Decimal) -> bool:
        return self.within_tolerance(
            grn_price,
            invoice_price,
            self.price_tolerance_percent,
        )

    def __str__(self):
        return f"PurchaseConfig ({self.company_id})"