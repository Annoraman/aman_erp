from datetime import date
from decimal import Decimal


class APAgingService:

    BUCKETS = {
        "current": (0, 0),
        "1_30": (1, 30),
        "31_60": (31, 60),
        "61_90": (61, 90),
        "90_plus": (91, 9999),
    }

    @staticmethod
    def calculate_age(due_date, today=None):
        today = today or date.today()
        return (today - due_date).days

    @classmethod
    def bucketize(cls, days_overdue):
        if days_overdue <= 0:
            return "current"
        elif 1 <= days_overdue <= 30:
            return "1_30"
        elif 31 <= days_overdue <= 60:
            return "31_60"
        elif 61 <= days_overdue <= 90:
            return "61_90"
        return "90_plus"