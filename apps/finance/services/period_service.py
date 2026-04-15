# apps/finance/services/period_service.py

from apps.finance.models.fiscal_period import FiscalPeriod

class PeriodService:

    @staticmethod
    def get_period(company, date):

        period = FiscalPeriod.objects.get(
            fiscal_year__company=company,
            start_date__lte=date,
            end_date__gte=date
        )

        if not period:
            raise ValueError("No fiscal period found for date")

        return period

    @staticmethod
    def close_period(period):

        if period.is_closed:
            raise ValueError("Period already closed")

        # Ensure all journals are posted
        unposted = period.journals.filter(is_posted=False).exists()

        if unposted:
            raise ValueError("Cannot close period with unposted journals")

        period.is_closed = True
        period.save()

        return period