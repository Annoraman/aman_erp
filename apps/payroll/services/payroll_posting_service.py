from decimal import Decimal

from apps.finance.models import JournalEntry, JournalLine


class PayrollPostingService:

    @staticmethod
    def post(payroll_run):

        for payslip in payroll_run.payslip_set.all():

            PayrollPostingService._post_payslip(payslip)

    @staticmethod
    def _post_payslip(payslip):

        entry = JournalEntry.objects.create(
            reference=f"Payroll {payslip.id}"
        )

        for line in payslip.lines.all():

            account = getattr(line, "account", None)

            if not account:
                continue

            if line.component_type == "ALLOWANCE":
                # Debit expense
                JournalLine.objects.create(
                    journal_entry=entry,
                    account=account,
                    debit=line.amount,
                    credit=Decimal("0.00"),
                )
            else:
                # Credit liability
                JournalLine.objects.create(
                    journal_entry=entry,
                    account=account,
                    debit=Decimal("0.00"),
                    credit=line.amount,
                )