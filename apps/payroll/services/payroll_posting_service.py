# apps/payroll/models/payroll_posting_service.py
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.finance.models import JournalEntry, JournalLine

class PayrollPostingService:

    @staticmethod
    @transaction.atomic
    def post(payroll_run):

        if payroll_run.status == "POSTED":
            raise ValidationError("Payroll already posted")

        for payslip in payroll_run.payslips.select_related("employee"):
            PayrollPostingService._post_payslip(payslip)

    @staticmethod
    def _post_payslip(self, payslip):

        entry = JournalEntry.objects.create(
            reference=f"Payroll {payslip.id}",
            company=payslip.company
        )

        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")

        for line in payslip.lines.select_related("component"):

            if component.component_type == "EARNING" and not component.account:
                raise ValidationError(f"Missing account for component {component.name}")

            # 🔥 RETRO LINE (no component)
            if line.code == "RETRO":

                payable_account = payslip.employee.payable_account

                if not payable_account:
                    raise ValidationError("Employee payable account missing")

                if line.amount > 0:
                    # increase payable
                    JournalLine.objects.create(
                        journal_entry=entry,
                        account=payable_account,
                        debit=Decimal("0.00"),
                        credit=line.amount,
                    )
                    total_credit += line.amount
                else:
                    # negative adjustment
                    JournalLine.objects.create(
                        journal_entry=entry,
                        account=payable_account,
                        debit=abs(line.amount),
                        credit=Decimal("0.00"),
                    )
                    total_debit += abs(line.amount)

                continue

            component = line.component

            if not component or not component.account:
                continue

            account = component.account
            amount = line.amount

            if component.component_type == "EARNING":
                JournalLine.objects.create(
                    journal_entry=entry,
                    account=account,
                    debit=amount,
                    credit=Decimal("0.00"),
                )
                total_debit += amount

            elif component.component_type == "DEDUCTION":
                JournalLine.objects.create(
                    journal_entry=entry,
                    account=account,
                    debit=Decimal("0.00"),
                    credit=amount,
                )
                total_credit += amount

        # 🔥 Net salary → payable (excluding retro already handled)
        payable_account = payslip.employee.payable_account

        if not payable_account:
            raise ValidationError("Employee payable account missing")

        retro_total = sum(
            l.amount for l in payslip.lines.all() if l.code == "RETRO"
                )

        net_salary = payslip.net_salary - retro_total

        JournalLine.objects.create(
            journal_entry=entry,
            account=payable_account,
            debit=Decimal("0.00"),
            credit=net_salary,
        )
        total_credit += net_salary

        # 🔥 Validate balance
        if total_debit != total_credit:
            raise ValidationError(
                f"Unbalanced entry for payslip {payslip.id}: "
                f"Dr={total_debit}, Cr={total_credit}"
            )