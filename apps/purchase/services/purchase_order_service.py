# apps/purchase/services/purchase_order_service.py

from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.purchase.models.purchase_order import PurchaseOrder
from apps.purchase.models.purchase_order_line import PurchaseOrderLine


class PurchaseOrderService:
    """
    ERP Service: Purchase Order Management
    Handles:
    - PO creation
    - Line creation
    - Status lifecycle updates
    """

    @staticmethod
    @transaction.atomic
    def create_po(*, supplier, items, company, user):
        # -------------------------
        # Supplier validation
        # -------------------------
        if supplier.company_id != company.id:
            raise ValidationError("Supplier does not belong to this company.")

        if not items:
            raise ValidationError("Purchase order must contain at least one item.")

        po = PurchaseOrder.objects.create(
            supplier=supplier,
            company=company,
            status="draft",
            created_by=user,
            total_amount=Decimal("0.00")
        )

        total_amount = Decimal("0.00")

        # -------------------------
        # Create PO lines
        # -------------------------
        for item in items:
            quantity = item.get("quantity")
            unit_price = item.get("unit_price")

            if quantity <= 0:
                raise ValidationError("Quantity must be greater than zero.")

            if unit_price < 0:
                raise ValidationError("Unit price cannot be negative.")

            line = PurchaseOrderLine.objects.create(
                purchase_order=po,
                product=item["product"],
                quantity=quantity,
                unit_price=unit_price,
                created_by=user
            )

            total_amount += line.quantity * line.unit_price

        # -------------------------
        # Update PO total
        # -------------------------
        po.total_amount = total_amount
        po.save(update_fields=["total_amount"])

        return po

    # -------------------------------------------------
    # ERP Lifecycle Rule Engine (Status Recalculation)
    # -------------------------------------------------
    @staticmethod
    def update_po_status(po):
        """
        Recalculate PO status based on receiving progress.
        """

        lines = po.lines.all()  # safer than reverse manager default name

        total_ordered = Decimal("0.00")
        total_received = Decimal("0.00")

        for line in lines:
            total_ordered += line.quantity
            total_received += line.received_quantity

        # -------------------------
        # Status rules (ERP standard)
        # -------------------------
        if total_received == 0:
            new_status = "approved"
        elif total_received < total_ordered:
            new_status = "partially_received"
        else:
            new_status = "fully_received"

        if po.status != new_status:
            po.status = new_status
            po.save(update_fields=["status"])

        return po