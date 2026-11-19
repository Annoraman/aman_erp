#Failure Rollback Test
import pytest
from django.core.exceptions import ValidationError

from apps.payroll.services.payroll_service import PayrollGenerationService


@pytest.mark.django_db
def test_payroll_atomicity(payroll_run, contract):

    contract.salary_structure = None
    contract.save()

    with pytest.raises(ValidationError):

        PayrollGenerationService.generate(payroll_run)

    assert payroll_run.payslips.count() == 0
