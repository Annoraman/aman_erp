#tests/integration/#test_payroll_generation.py
import pytest
from apps.hr.models.contract import Contract
from apps.payroll.services.payroll_service import PayrollGenerationService
from apps.payroll.tests.factories.hr_factories import ContractFactory
from apps.payroll.tests.factories.payroll_factories import SalaryStructureFactory


@pytest.mark.django_db
def test_full_payroll_generation(payroll_run, company):

    salary_structure = SalaryStructureFactory(company=company)

    contract1 = ContractFactory(
        company=company,
        salary_structure=salary_structure,
        status=Contract.Status.ACTIVE
    )

    contract2 = ContractFactory(
        company=company,
        salary_structure=salary_structure,
        status=Contract.Status.ACTIVE
    )

    result = PayrollGenerationService.generate(payroll_run)

    assert payroll_run.payslips.count() == 2