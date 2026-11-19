from datetime import date
from decimal import Decimal

from apps.finance.services import APAgingService


class APAgingReportService:

    @staticmethod
    def generate_as_of(date_from=None):
        from apps.purchase.models import SupplierInvoice

        today = date_from or date.today()

        invoices = SupplierInvoice.objects.filter(
            is_posted=True
        ).select_related("vendor")

        report = {}

        for inv in invoices:
            open_amount = inv.total_amount - inv.paid_amount
            if open_amount <= 0:
                continue

            days_overdue = (today - inv.due_date).days
            bucket = APAgingService.bucketize(days_overdue)

            vendor_id = inv.vendor_id

            if vendor_id not in report:
                report[vendor_id] = {
                    "vendor": inv.vendor.name,
                    "current": Decimal("0"),
                    "1_30": Decimal("0"),
                    "31_60": Decimal("0"),
                    "61_90": Decimal("0"),
                    "90_plus": Decimal("0"),
                    "total": Decimal("0"),
                }

            report[vendor_id][bucket] += open_amount
            report[vendor_id]["total"] += open_amount

        return report