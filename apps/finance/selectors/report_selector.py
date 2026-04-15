# apps/finance/selectors/report_selector.py

from apps.finance.models import JournalLine
from django.db.models import Sum

class ReportSelector:

    @staticmethod
    def trial_balance():
        """
        Returns: list of accounts with total debit & credit
        """
        return (
            JournalLine.objects
            .filter(journal__is_posted=True)
            .values("account__code", "account__name")
            .annotate(
                total_debit=Sum("debit"),
                total_credit=Sum("credit")
            )
            .order_by("account__code")
        )

    @staticmethod
    def income_statement():
        """
        Returns total income, total expenses, and net profit
        """
        
        income_lines = JournalLine.objects.filter(
            journal__is_posted=True,
            account__type="INCOME"
        ).aggregate(total_income=Sum("credit") - Sum("debit"))

        expense_lines = JournalLine.objects.filter(
            journal__is_posted=True,
            account__type="EXPENSE"
        ).aggregate(total_expense=Sum("debit") - Sum("credit"))

        net_profit = (income_lines["total_income"] or 0) - (expense_lines["total_expense"] or 0)

        return {
                "total_income": income_lines["total_income"] or 0,
                "total_expense": expense_lines["total_expense"] or 0,
                "net_profit": net_profit
            }

    @staticmethod
    def balance_sheet():
        from apps.finance.models import JournalLine

        assets = JournalLine.objects.filter(
            journal__is_posted=True,
            account__type="ASSET"
        ).aggregate(total_assets=Sum("debit") - Sum("credit"))

        liabilities = JournalLine.objects.filter(
            journal__is_posted=True,
            account__type="LIABILITY"
        ).aggregate(total_liabilities=Sum("credit") - Sum("debit"))

        equity = JournalLine.objects.filter(
            journal__is_posted=True,
            account__type="EQUITY"
        ).aggregate(total_equity=Sum("credit") - Sum("debit"))

        return {
            "assets": assets["total_assets"] or 0,
            "liabilities": liabilities["total_liabilities"] or 0,
            "equity": equity["total_equity"] or 0,
            "check": (assets["total_assets"] or 0) - ((liabilities["total_liabilities"] or 0) + (equity["total_equity"] or 0))
        }

    from django.db.models import Sum
from apps.finance.models import JournalLine


class ReportSelector:

    @staticmethod
    def trial_balance(company):
        return (
            JournalLine.objects
            .filter(
                journal__is_posted=True,
                journal__company=company
            )
            .values("account__code", "account__name")
            .annotate(
                total_debit=Sum("debit"),
                total_credit=Sum("credit")
            )
        )

    @staticmethod
    def cost_center_report(company):
        return (
            JournalLine.objects
            .filter(
                journal__is_posted=True,
                journal__company=company
            )
            .values("cost_center__name")
            .annotate(
                total_debit=Sum("debit"),
                total_credit=Sum("credit")
            )
        )