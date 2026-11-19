# payroll/tests/factories.py
import factory
from apps.accounts.models.user import User
from apps.payroll.models.payroll_run import PayrollRun
from apps.payroll.tests.factories.common_factories import CompanyFactory
from apps.payroll.tests.factories.payroll_factories import PayrollPeriodFactory



class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@test.com")


    
class CompanyAwareFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        abstract = True

    company = factory.SubFactory(CompanyFactory)
       
# class EmployeeFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = Employee

#     company = factory.SubFactory(CompanyFactory)
#     created_by = factory.SubFactory(UserFactory)

#     first_name = "Test"
#     last_name = factory.Sequence(lambda n: f"User{n}")
#     hire_date = "2026-01-01"


class PayrollRunFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PayrollRun

    company = factory.SubFactory(CompanyFactory)

    status = PayrollRun.DRAFT
    
    period = factory.SubFactory(
        PayrollPeriodFactory
        )

