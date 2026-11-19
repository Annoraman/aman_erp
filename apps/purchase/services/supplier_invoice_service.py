from django.db import transaction
from django.core.exceptions import ValidationError

from apps.finance.services.journal_service import JournalService
from apps.purchase.models import GoodsReceiptLine, PurchaseConfig
from apps.purchase.domain.supplier_invoice import SupplierInvoice
from apps.purchase.models.supplier_invoice_line import SupplierInvoiceLine


class SupplierInvoiceService:

    # =====================================================
    # CREATE INVOICE
    # =====================================================
    @staticmethod
    @transaction.atomic
    def create_invoice(*, supplier, items, company, user):

        if supplier.company_id != company.id:
            raise ValidationError("Supplier company mismatch.")

        if not items:
            raise ValidationError("Invoice must contain at least one line.")

        invoice = SupplierInvoice(supplier, company, user)

        for item in items:

            grn_line = (
                GoodsReceiptLine.objects
                .select_for_update()
                .select_related("purchase_order_line", "grn")
                .get(id=item["grn_line"].id)
            )

            quantity = item["quantity"]
            unit_price = item["unit_price"]

            if grn_line.grn.company_id != company.id:
                raise ValidationError("GRN company mismatch.")

            # DOMAIN RULE INSIDE AGGREGATE
            invoice.add_line(grn_line, quantity, unit_price)

        # -------------------------
        # Load config
        # -------------------------
        config = PurchaseConfig.objects.filter(company=company).first()

        invoice.status = invoice.calculate_status(config)

        # -------------------------
        # PERSIST (simplified)
        # -------------------------
        invoice_obj = SupplierInvoice.objects.create(
            supplier=supplier,
            company=company,
            status=invoice.status,
            created_by=user,
            total_amount=invoice.total_amount
        )

        # create lines
        for line in invoice.lines:
            line["grn_line"].invoiced_quantity += line["quantity"]
            line["grn_line"].save(update_fields=["invoiced_quantity"])

            po_line = line["grn_line"].purchase_order_line
            po_line.invoiced_quantity += line["quantity"]
            po_line.save(update_fields=["invoiced_quantity"])

            SupplierInvoiceLine.objects.create(
                invoice=invoice_obj,
                grn_line=line["grn_line"],
                invoiced_quantity=line["quantity"],
                unit_price=line["unit_price"],
                created_by=user
            )

        return invoice_obj

    # =====================================================
    # POST INVOICE
    # =====================================================
    @staticmethod
    @transaction.atomic
    def post_invoice(*, invoice, user):

        config = PurchaseConfig.objects.filter(company=invoice.company).first()

        if not invoice.can_post():
            raise ValidationError("Invoice not eligible for posting.")

        if not invoice.supplier.account_id:
            raise ValidationError("Supplier account not configured.")

        if not config or not config.grni_account:
            raise ValidationError("GRNI account not configured.")

        entry = JournalService.create_entry(
            date=invoice.invoice_date or invoice.created_at,
            description=f"Supplier Invoice #{invoice.id}",
            lines=[
                {
                    "account": config.grni_account,
                    "debit": invoice.total_amount,
                },
                {
                    "account": invoice.supplier.account,
                    "credit": invoice.total_amount,
                }
            ],
            created_by=user
        )

        invoice.mark_posted(entry)

        invoice.save(update_fields=["status", "journal_entry"])

        return invoice