#conftest
import pytest
from apps.payroll.models import PayrollRun, PayrollPeriod
from core.tests.factories import CompanyFactory, UserFactory
from django.contrib.auth import get_user_model
from apps.payroll.te_sts_old.factories import ContractFactory, EmployeeFactory

User = get_user_model()


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def company(db, user):
    return CompanyFactory(created_by=user)


@pytest.fixture
def payroll_period(db):
    return PayrollPeriod.objects.create(
        start_date="2026-06-01",
        end_date="2026-06-30"
    )


@pytest.fixture
def payroll_run(db, company, payroll_period):
    return PayrollRun.objects.create(
        company=company,
        period=payroll_period,
        status=PayrollRun.DRAFT,
        notes="Test run",
        created_by_id = user
    )
    
    
@pytest.fixture
def employee(db, user, company):
    return EmployeeFactory(company=company)


@pytest.fixture
def contract(db, employee):
    return ContractFactory(
        employee=employee
    )