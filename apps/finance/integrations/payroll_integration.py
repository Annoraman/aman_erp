# apps/finance/integrations/payroll_integration.py

from apps.finance.services.journal_service import JournalService
from apps.finance.models import Account
from apps.payroll.models import payslip

class PayrollAccountingIntegration:

    @staticmethod
    def create_journal_from_payslip(payslip, user):

        lines = []

        # 1️⃣ Salary Expense
        salary_account = Account.objects.get(code="5000")  # example: Salary Expense
        lines.append({
            "account": salary_account,
            "debit": payslip.gross_salary,
            "credit": 0
        })

        # 2️⃣ Allowances
        for allowance in payslip.allowances.all():
            allowance_account = Account.objects.get(code=allowance.account_code)
            lines.append({
                "account": allowance_account,
                "debit": allowance.amount,
                "credit": 0
            })

        # 3️⃣ Tax Payable
        tax_account = Account.objects.get(code="2100")  # example: Tax Payable
        if payslip.tax_amount > 0:
            lines.append({
                "account": tax_account,
                "debit": 0,
                "credit": payslip.tax_amount
            })

        # 4️⃣ Net Payable to Employee
        payable_account = Account.objects.get(code="2200")  # Employee Payable
        lines.append({
            "account": payable_account,
            "debit": 0,
            "credit": payslip.net_salary
        })

        # 5️⃣ Create journal entry
        journal_data = {
            "date": payslip.date,
            "description": f"Payroll for {payslip.employee}",
            "lines": lines
        }

        return JournalService.create_journal(user, journal_data)

    journal_data = {
        "date": payslip.date,
        "description": f"Payroll - {payslip.employee}",
        "company": payslip.company,
        "lines": [
            {
                "account": salary_account,
                "debit": payslip.gross_salary,
                "cost_center": payslip.department_cost_center
            },
            ...
        ]
    }