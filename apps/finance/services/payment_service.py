"""
-- description
Vendor Payment Flow:
Vendor Bill → AP → Pay → Payment → Journal

Customer Receipt Flow:
Invoice → AR → Receive → Payment → Journal
"""



# apps/finance/services/payment_service.py

from apps.finance.services.journal_service import JournalService

class PaymentService:

    @staticmethod
    def process_payment(user, payment):

        if payment.is_posted:
            raise ValueError("Payment already processed")

        if payment.payment_type == "PAY":
            # Pay Vendor
            payable_account = payment.vendor.payable_account

            lines = [
                {
                    "account": payable_account,
                    "debit": payment.amount,
                },
                {
                    "account": payment.method.account,
                    "credit": payment.amount,
                }
            ]

        elif payment.payment_type == "RECEIVE":
            # Receive Customer
            receivable_account = payment.customer.receivable_account

            lines = [
                {
                    "account": payment.method.account,
                    "debit": payment.amount,
                },
                {
                    "account": receivable_account,
                    "credit": payment.amount,
                }
            ]

        else:
            raise ValueError("Invalid payment type")

        journal = JournalService.create_journal(user, {
            "date": payment.date,
            "description": f"Payment - {payment.id}",
            "company": payment.company,
            "lines": lines
        })

        payment.journal = journal
        payment.is_posted = True
        payment.save()

        return payment