# apps/finance/services/year_end_service.py

class YearEndService:

    @staticmethod
    def close_year(fiscal_year, retained_earnings_account, user):

        from apps.finance.selectors.report_selector import ReportSelector
        from apps.finance.services.journal_service import JournalService

        report = ReportSelector.income_statement()

        net_profit = report["net_profit"]

        if net_profit == 0:
            return None

        lines = []

        if net_profit > 0:
            # Profit
            lines.append({
                "account": retained_earnings_account,
                "credit": net_profit
            })
        else:
            # Loss
            lines.append({
                "account": retained_earnings_account,
                "debit": abs(net_profit)
            })

        return JournalService.create_journal(user, {
            "date": fiscal_year.end_date,
            "description": "Year End Closing",
            "company": fiscal_year.company,
            "lines": lines
        })