from django.db import models
from django.core.exceptions import ValidationError

from core.models.base import CompanyAwareModel


class Supplier(CompanyAwareModel):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)

    account = models.ForeignKey(
        "finance.Account",
        on_delete=models.PROTECT,
    )

    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.PROTECT,
    )

    is_active = models.BooleanField(default=True)

    credit_limit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    class Meta:
        db_table = "suppliers"
        unique_together = ("company", "code")
        indexes = [
            models.Index(fields=["company", "code"]),
            models.Index(fields=["company", "is_active"]),
        ]
        ordering = ["name"]

    # -------------------------
    # Validation
    # -------------------------
    def clean(self):
        super().clean()

        if self.account and self.account.company_id != self.company_id:
            raise ValidationError("Account must belong to same company")

        if self.credit_limit < 0:
            raise ValidationError("Credit limit cannot be negative")

    # -------------------------
    # Domain Behavior
    # -------------------------
    def deactivate(self):
        self.is_active = False

    def activate(self):
        self.is_active = True

    # -------------------------
    def __str__(self):
        return f"{self.code} - {self.name}"


# =========================================================
# Supplier Address
# =========================================================

class SupplierAddress(CompanyAwareModel):
    supplier = models.ForeignKey(
        "purchase.Supplier",
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    address = models.TextField()

    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "supplier_addresses"
        indexes = [
            models.Index(fields=["company", "supplier"]),
        ]

    def clean(self):
        super().clean()

        if self.supplier.company_id != self.company_id:
            raise ValidationError("Supplier company mismatch")


# =========================================================
# Supplier Contact
# =========================================================

class SupplierContact(CompanyAwareModel):
    supplier = models.ForeignKey(
        "purchase.Supplier",
        on_delete=models.CASCADE,
        related_name="contacts",
    )

    name = models.CharField(max_length=255)

    phone = models.CharField(max_length=50, blank=True)

    email = models.EmailField(blank=True)

    class Meta:
        db_table = "supplier_contacts"
        indexes = [
            models.Index(fields=["company", "supplier"]),
        ]

    def clean(self):
        super().clean()

        if self.supplier.company_id != self.company_id:
            raise ValidationError("Supplier company mismatch")