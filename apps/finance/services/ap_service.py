"""
-- description
“AP Service (Posting Bill)” is an Accounts Payable function that records a supplier invoice (bill) into the accounting system.

It does this by:

Creating a payable (money you owe to a vendor)
Posting accounting entries to the general ledger
Updating vendor balance and liabilities
Making the bill ready for payment processing later

In simple terms: it turns a supplier invoice into an official accounting record inside your ERP system.

Vendor Bill → AP Service → Journal Entry → GL
"""
# apps/finance/services/ap_service.py

from apps.finance.services.journal_service import JournalService

class APService:

    @staticmethod
    def post_vendor_bill(user, bill):

        if bill.is_posted:
            raise ValueError("Already posted")

        expense_account = ...  # from bill lines (future extension)

        lines = [
            # Expense
            {
                "account": expense_account,
                "debit": bill.total_amount,
            },
            # Vendor Payable
            {
                "account": bill.vendor.payable_account,
                "credit": bill.total_amount,
            }
        ]

        journal = JournalService.create_journal(user, {
            "date": bill.date,
            "description": f"Vendor Bill - {bill.vendor}",
            "company": bill.company,
            "lines": lines
        })

        bill.journal = journal
        bill.is_posted = True
        bill.save()

        return bill