#apps\payroll\tests\integration\test_payroll_generation.py
import pytest
from apps.hr.models.contract import Contract
from apps.payroll.tests.factories.payroll_factories import PayrollPeriodFactory, SalaryRuleFactory, SalaryRuleVersionFactory
from apps.payroll.tests.factory import PayrollRunFactory, CompanyFactory
from apps.payroll.services.payroll_service import PayrollGenerationService
from apps.payroll.tests.factories.hr_factories import ContractFactory, EmployeeFactory


@pytest.mark.django_db
def test_full_payroll_generation():
    company = CompanyFactory()
    
    employee = EmployeeFactory(company=company)
    period = PayrollPeriodFactory()
    
    contract = ContractFactory(
        employee=employee,
        company=company,
        status=Contract.Status.ACTIVE
        
    )

    payroll_run = PayrollRunFactory(
        company=company,
        period = period
    )

    # result = PayrollGenerationService.generate(payroll_run)
    salary_structure = contract.salary_structure

    rule = SalaryRuleFactory(
        salary_structure=salary_structure,
        company=company
    )

    SalaryRuleVersionFactory(
        rule=rule,
        company=company,
    )
    try:
        PayrollGenerationService.generate(payroll_run)
    except Exception as e:
        print(type(e))
        print(e)
        raise

    assert payroll_run.payslips.count() == 1