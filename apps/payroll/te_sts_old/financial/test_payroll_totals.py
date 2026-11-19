#tests/financial/test_payroll_totals.py
import pytest
from decimal import Decimal
from apps.payroll.services.payroll_service import PayrollGenerationService


@pytest.mark.django_db
def test_gross_equals_sum_of_lines(payroll_run):

    PayrollGenerationService.generate(payroll_run)

    for payslip in payroll_run.payslips.all():

        lines_sum = sum(
            line.amount for line in payslip.lines.all()
        )

        assert payslip.gross_salary == Decimal(lines_sum)