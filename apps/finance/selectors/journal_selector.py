# apps/finance/selectors/journal_selector.py

from django.db.models import Sum
from apps.finance.models import JournalEntry, JournalLine
from django.db.models.functions import Coalesce
from django.db.models import Value


class JournalSelector:

    @staticmethod
    def get_posted_journals():
        return JournalEntry.objects.filter(is_posted=True)

    @staticmethod
    def get_by_date_range(start_date, end_date):
        return JournalEntry.objects.filter(
            date__range=(start_date, end_date)
        )

    @staticmethod
    def trial_balance(company):
        """
        Returns:
            [
                {
                    account__code,
                    account__name,
                    total_debit,
                    total_credit
                }
            ]
        """
        return (
            JournalLine.objects
            .filter(
                journal__is_posted=True,
                journal__company=company
            )
            .values("account__code", "account__name")
            .annotate(
                total_debit=Coalesce(Sum("debit"), Value(0)),
                total_credit=Coalesce(Sum("credit"), Value(0)),
            )
            .order_by("account__code")
        )

    @staticmethod
    def account_ledger(company, account, start_date=None, end_date=None):

        qs = JournalLine.objects.filter(
            journal__is_posted=True,
            journal__company=company,
            account=account
        ).select_related("journal")

        if start_date and end_date:
            qs = qs.filter(journal__date__range=(start_date, end_date))

        return qs.order_by("journal__date", "id")

    @staticmethod
    def get_account_ledger(company, account, start_date, end_date):

        lines = (
            JournalLine.objects
            .filter(
                journal__company=company,
                journal__is_posted=True,
                account=account,
                journal__date__range=(start_date, end_date)
            )
            .select_related("journal")
            .order_by("journal__date", "id")
        )

        result = []
        balance = 0

        for line in lines:
            balance += line.debit - line.credit

            result.append({
                "date": line.journal.date,
                "description": line.journal.description,
                "debit": line.debit,
                "credit": line.credit,
                "balance": balance
            })

        return result

    @staticmethod
    def income_statement(company, start_date, end_date):

        from apps.finance.models import JournalLine

        data = (
            JournalLine.objects
            .filter(
                journal__company=company,
                journal__is_posted=True,
                journal__date__range=(start_date, end_date),
                account__type__in=["INCOME", "EXPENSE"]
            )
            .values("account__type")
            .annotate(
                total_debit=Sum("debit"),
                total_credit=Sum("credit")
            )
        )

        income = 0
        expense = 0

        for row in data:
            if row["account__type"] == "INCOME":
                income += row["total_credit"] - row["total_debit"]
            elif row["account__type"] == "EXPENSE":
                expense += row["total_debit"] - row["total_credit"]

        return {
            "income": income,
            "expense": expense,
            "net_profit": income - expense
        }

    @staticmethod
    def balance_sheet(company):

        from apps.finance.models import JournalLine

        data = (
            JournalLine.objects
            .filter(
                journal__company=company,
                journal__is_posted=True
            )
            .values("account__type")
            .annotate(
                total_debit=Sum("debit"),
                total_credit=Sum("credit")
            )
        )

        assets = 0
        liabilities = 0
        equity = 0

        for row in data:
            acc_type = row["account__type"]
            debit = row["total_debit"] or 0
            credit = row["total_credit"] or 0

            if acc_type == "ASSET":
                assets += debit - credit

            elif acc_type == "LIABILITY":
                liabilities += credit - debit

            elif acc_type == "EQUITY":
                equity += credit - debit

        return {
            "assets": assets,
            "liabilities": liabilities,
            "equity": equity,
            "balanced": assets == (liabilities + equity)
        }

