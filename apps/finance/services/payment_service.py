"""
-- description
Vendor Payment Flow:
Vendor Bill → AP → Pay → Payment → Journal

Customer Receipt Flow:
Invoice → AR → Receive → Payment → Journal
"""

# apps/finance/services/payment_service.py

from django.db import transaction
from django.core.exceptions import ValidationError

from apps.finance.models.payment import Payment
from apps.finance.models.payment_allocation import PaymentAllocation
from apps.finance.services import JournalService


class PaymentService:

    @staticmethod
    @transaction.atomic
    def create_payment(*, supplier, invoices, company, user, payment_date):

        total = sum(i["amount"] for i in invoices)

        payment = Payment.objects.create(
            supplier=supplier,
            company=company,
            amount=total,
            payment_date=payment_date,
            currency=supplier.currency,
            created_by=user
        )

        for item in invoices:
            invoice = item["invoice"]
            amount = item["amount"]

            if invoice.company != company:
                raise ValidationError("Company mismatch")

            if invoice.status not in ["posted", "partially_paid"]:
                raise ValidationError("Invoice not payable")

            if payment.amount <= 0:
                raise ValidationError("Invalid payment amount")

            if invoice.paid_amount >= invoice.total_amount:
                 raise ValidationError("Invoice already paid")

            remaining = invoice.total_amount - invoice.paid_amount

            if amount > remaining:
                raise ValidationError("Overpayment not allowed")

            PaymentAllocation.objects.create(
                payment=payment,
                invoice=invoice,
                allocated_amount=amount,
                created_by=user
            )

        return payment
    @staticmethod
    @transaction.atomic
    def post_payment(payment, user):

        # 🔒 lock payment row
        payment = (
            payment.__class__.objects
            .select_for_update()
            .select_related("supplier", "method")
            .get(pk=payment.pk)
        )

        # 🔒 basic validations
        if payment.is_posted:
            raise ValidationError("Payment already posted")

        if payment.payment_type != "PAY":
            raise ValidationError("Only supplier payments supported")

        if not payment.supplier:
            raise ValidationError("Supplier is required")

        if not payment.method or not hasattr(payment.method, "account"):
            raise ValidationError("Payment method must have account")

        supplier_account = payment.supplier.account
        bank_account = payment.method.account

        # 🔥 load allocations efficiently
        allocations = payment.allocations.select_related("invoice")

        total_allocated = sum(a.amount for a in allocations)

        # 🔒 accounting integrity check
        if total_allocated != payment.amount:
            raise ValidationError("Allocation total must equal payment amount")

        # 🔥 validate allocations BEFORE posting
        for alloc in allocations:
            invoice = alloc.invoice

            if invoice.company != payment.company:
                raise ValidationError("Company mismatch")

            remaining = invoice.total_amount - invoice.paid_amount

            if alloc.amount > remaining:
                raise ValidationError(
                    f"Overpayment detected for invoice {invoice.id}"
                )

        # 🔥 create journal entry
        entry = JournalService.create_entry(
            date=payment.date,
            description=f"Payment #{payment.id}",
            lines=[
                {"account": supplier_account, "debit": payment.amount},
                {"account": bank_account, "credit": payment.amount},
            ],
            created_by=user
        )

        # 🔥 apply allocations
        for alloc in allocations:
            invoice = alloc.invoice

            invoice.paid_amount += alloc.amount

            if invoice.paid_amount == invoice.total_amount:
                invoice.status = "paid"
            else:
                invoice.status = "partially_paid"

            invoice.save(update_fields=["paid_amount", "status"])

        # 🔥 finalize
        payment.journal = entry
        payment.is_posted = True
        payment.save(update_fields=["journal", "is_posted"])

        return payment