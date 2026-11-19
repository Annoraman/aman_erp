#apps\payroll\tests\factories\finance_factories.py
import factory
from apps.finance.models.account import Account
from apps.payroll.tests.factory import CompanyFactory


class AccountFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Account

    code = factory.Sequence(
        lambda n: f"ACC{n:04d}"
    )

    name = factory.Sequence(
        lambda n: f"Account {n}"
    )

    type = "EXPENSE"

    company = factory.SubFactory(CompanyFactory)
    
    is_active = True