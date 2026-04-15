# apps/finance/services/ar_service.py

"""
-- description
“AR Service” stands for Accounts Receivable Service.

It is responsible for managing money that customers owe to your company.

It does this by:

Creating customer invoices (sales bills)
Recording receivables (money expected from customers)
Posting accounting entries to the general ledger
Tracking customer balances and due payments
Managing collections when customers pay

In simple terms:
It turns sales into “money you will receive” and tracks what customers still owe your business.

Invoice → AR Service → Journal Entry → GL
"""

from apps.finance.services.journal_service import JournalService


class ARService:

    @staticmethod
    def post_invoice(user, invoice):

        if invoice.is_posted:
            raise ValueError("Already posted")

        revenue_account = ...  # from invoice lines

        lines = [
            # Customer Receivable
            {
                "account": invoice.customer.receivable_account,
                "debit": invoice.total_amount,
            },
            # Revenue
            {
                "account": revenue_account,
                "credit": invoice.total_amount,
            }
        ]

        journal = JournalService.create_journal(user, {
            "date": invoice.date,
            "description": f"Invoice - {invoice.customer}",
            "company": invoice.company,
            "lines": lines
        })

        invoice.journal = journal
        invoice.is_posted = True
        invoice.save()

        return invoice