import pytest

from apps.hr.models.contract import Contract
from apps.payroll.services.payroll_service import PayrollGenerationService
from apps.payroll.tests.factories.hr_factories import ContractFactory
from apps.payroll.tests.factories.payroll_factories import SalaryRuleFactory, SalaryRuleVersionFactory
from apps.payroll.tests.factory import PayrollRunFactory


@pytest.mark.django_db
def test_inactive_contract_skipped():

    active_contract = ContractFactory(
        status=Contract.Status.ACTIVE
    )

    ContractFactory(
        status=Contract.Status.TERMINATED,
        company=active_contract.company
    )

    rule = SalaryRuleFactory(
        salary_structure=active_contract.salary_structure
    )

    SalaryRuleVersionFactory(
        rule=rule
    )

    payroll_run = PayrollRunFactory(
        company=active_contract.company
    )

    PayrollGenerationService.generate(
        payroll_run
    )

    assert payroll_run.payslips.count() == 1