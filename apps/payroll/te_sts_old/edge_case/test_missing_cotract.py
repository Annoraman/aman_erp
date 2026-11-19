#missing contract
import pytest
from django.core.exceptions import ValidationError

from apps.payroll.services.payroll_service import PayrollGenerationService


@pytest.mark.django_db
def test_no_contract_fails(payroll_run):

    with pytest.raises(ValidationError):
        PayrollGenerationService.generate(payroll_run)
