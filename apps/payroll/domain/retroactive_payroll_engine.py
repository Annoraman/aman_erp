# apps/payroll/domain/retroactive_engine.py
from decimal import Decimal


class RetroactivePayrollEngine:

    @staticmethod
    def calculate_differences(old_payslip, new_result):

        differences = []

        # -----------------------------------
        # OLD LINES MAP
        # -----------------------------------
        old_lines_map = {
            line.code: line
            for line in old_payslip.lines.all()
        }

        # -----------------------------------
        # NEW LINES
        # -----------------------------------
        for new_line in new_result["lines"]:

            code = new_line["code"]

            old_amount = Decimal("0.00")
            new_amount = Decimal(new_line["amount"])

            # old value
            if code in old_lines_map:
                old_amount = Decimal(old_lines_map[code].amount)

            difference = new_amount - old_amount

            # skip unchanged lines
            if difference == 0:
                continue

            differences.append({
                "code": code,
                "component": new_line["component"],
                "old_amount": old_amount,
                "new_amount": new_amount,
                "difference": difference,
                "type": new_line["type"],
            })

        # -----------------------------------
        # TOTALS
        # -----------------------------------
        total_difference = sum(
            item["difference"]
            for item in differences
        )

        return {
            "differences": differences,
            "total_difference": total_difference,
        }