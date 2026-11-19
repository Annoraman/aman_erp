# core/services/exchange_rate_service.py

from decimal import Decimal
from django.utils import timezone
from core.models import ExchangeRate


class ExchangeRateService:

    @staticmethod
    def get_rate(from_currency, to_currency, date=None):
        if from_currency == to_currency:
            return Decimal("1")

        date = date or timezone.now().date()

        rate = (
            ExchangeRate.objects
            .filter(
                from_currency=from_currency,
                to_currency=to_currency,
                date__lte=date,
                is_active=True
            )
            .order_by("-date")
            .first()
        )

        if not rate:
            raise ValueError("Exchange rate not found")

        return rate.rate