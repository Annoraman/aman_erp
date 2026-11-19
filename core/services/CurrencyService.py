from decimal import Decimal, ROUND_HALF_UP

from core.services.exchange_rate_service import ExchangeRateService


class CurrencyService:

    @staticmethod
    def convert(amount, from_currency, to_currency, date=None):

        rate = ExchangeRateService.get_rate(
            from_currency,
            to_currency,
            date
        )

        result = Decimal(amount) * rate

        return result.quantize(
            Decimal(f"1.{'0'*to_currency.decimal_places}"),
            rounding=ROUND_HALF_UP
        )