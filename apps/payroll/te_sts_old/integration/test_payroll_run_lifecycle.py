#tests/integration/test_payroll_run_lifecycle.py
import pytest

from apps.payroll.models import PayrollRun
from apps.payroll.services.payroll_service import PayrollGenerationService


@pytest.mark.django_db
def test_payroll_run_status_flow(payroll_run, contract):

    PayrollGenerationService.generate(payroll_run)

    payroll_run.refresh_from_db()

    assert payroll_run.status == PayrollRun.DRAFT
    assert payroll_run.payslips.exists()
