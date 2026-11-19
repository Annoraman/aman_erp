# apps/purchase/services/goods_receipt_service.py

from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.purchase.models import GoodsReceipt
from apps.purchase.models.purchase_config import PurchaseConfig
from apps.finance.services.journal_service import JournalService

from apps.inventory.models import Stock, StockMovement


class GoodsReceiptService:
    """
    ERP Service: Goods Receipt Posting (GRN)
    Handles:
    - PO receiving updates
    - Stock updates
    - Stock movements
    - Accounting entries (GRNI clearing)
    """

    @staticmethod
    @transaction.atomic
    def process_grn(grn: GoodsReceipt, user):
        if grn.status == "posted":
            raise ValidationError("GRN is already posted.")

        company = grn.company
        warehouse = grn.warehouse

        total_value = Decimal("0.00")
        inventory_account_map = {}

        lines = (
            grn.lines
            .select_related("po_line", "product")
            .select_for_update()
        )

        for line in lines:
            po_line = line.po_line

            # -------------------------
            # Company validation
            # -------------------------
            if po_line.company_id != company.id:
                raise ValidationError(
                    f"Line {line.id}: Company mismatch with PO line"
                )

            # -------------------------
            # Over-receiving validation
            # -------------------------
            new_received_qty = po_line.received_quantity + line.quantity

            if new_received_qty > po_line.ordered_quantity:
                raise ValidationError(
                    f"Line {line.id}: Receiving quantity exceeds PO limit"
                )

            # -------------------------
            # Update PO line
            # -------------------------
            po_line.received_quantity = new_received_qty
            po_line.save(update_fields=["received_quantity"])

            # -------------------------
            # Stock update (safe get_or_create)
            # -------------------------
            stock, _ = Stock.objects.select_for_update().get_or_create(
                company=company,
                product=line.product,
                warehouse=warehouse,
                defaults={"quantity": Decimal("0.00")}
            )

            stock.quantity += line.quantity
            stock.save(update_fields=["quantity"])

            # -------------------------
            # Stock movement (audit trail)
            # -------------------------
            StockMovement.objects.create(
                company=company,
                product=line.product,
                warehouse=warehouse,
                quantity=line.quantity,
                movement_type="grn",
                reference=f"GRN-{grn.id}"
            )

            # -------------------------
            # Accumulate value safely
            # -------------------------
            line_value = line.quantity * po_line.unit_price
            total_value += line_value

            # store product account reference (avoid loop overwrite issue)
            inventory_account_map[line.product.inventory_account_id] = True

        # -------------------------
        # Load accounting config
        # -------------------------
        try:
            config = PurchaseConfig.objects.get(company=company)
        except PurchaseConfig.DoesNotExist:
            raise ValidationError("Purchase configuration not found.")

        if not config.grni_account:
            raise ValidationError("GRNI account is not configured.")

        # -------------------------
        # Accounting entry (GRN posting)
        # -------------------------
        JournalService.create_entry(
            date=grn.received_at,
            description=f"Goods Receipt Note #{grn.id}",
            lines=[
                {
                    "account": list(inventory_account_map.keys())[0],
                    "debit": total_value,
                },
                {
                    "account": config.grni_account,
                    "credit": total_value,
                },
            ],
            created_by=user
        )

        # -------------------------
        # Finalize GRN
        # -------------------------
        grn.status = "posted"
        grn.posted_by = user
        grn.save(update_fields=["status", "posted_by"])

        return grn