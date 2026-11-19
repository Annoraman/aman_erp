#factories/payroll_factories.py

import factory

from apps.payroll.models import (
    PayrollRun,
    PayrollPeriod,
    Payslip,
    PayslipLine,
    SalaryStructure,
)
from apps.payroll.models.salary_component import SalaryComponent
from apps.payroll.models.salary_rule import SalaryRule
from apps.payroll.models.salary_rule_version import SalaryRuleVersion
from apps.payroll.tests.factories.finance_factories import AccountFactory
from apps.payroll.tests.factory import CompanyFactory



class PayrollPeriodFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = PayrollPeriod

    start_date = "2026-06-01"
    end_date = "2026-06-30"

    is_closed = False
    

class PayrollRunFactory(factory.django.DjangoModelFactory):
    
    period = factory.SubFactory(PayrollPeriodFactory)
    status = PayrollRun.DRAFT
    company = factory.SubFactory(CompanyFactory)
    class Meta:
        model = PayrollRun

class PayslipFactory(factory.django.DjangoModelFactory):
    
    name = factory.Sequence(
        lambda n: f"Structure-{n}"
    )

    description = "Test Structure"

    is_active = True

    class Meta:
        model = Payslip


class PayslipLineFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = PayslipLine
        

class SalaryStructureFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = SalaryStructure

    company = factory.SubFactory(
        CompanyFactory
    )

    name = factory.Sequence(
        lambda n: f"Structure-{n}"
    )

    description = "Test Salary Structure"

    is_active = True
#-----------------------------------------------------------------------------
# payroll_factories.py

class SalaryComponentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = SalaryComponent

    code = factory.Sequence(
        lambda n: f"BASIC{n}"
    )

    name = factory.Sequence(
        lambda n: f"Basic Salary {n}"
    )

    component_type = SalaryComponent.Type.EARNING

    account = factory.SubFactory(
        AccountFactory
    )

    company = factory.SelfAttribute(
        "account.company"
    )

    created_by = factory.SelfAttribute(
        "account.created_by"
    )

    is_active = True

    
class SalaryRuleFactory(factory.django.DjangoModelFactory):
        
    class Meta:
        model = SalaryRule

    salary_structure = factory.SubFactory(
           SalaryStructureFactory
        )

    component = factory.SubFactory(
            SalaryComponentFactory
        )

    company = factory.SelfAttribute(
            "salary_structure.company"
        )

    created_by = factory.SelfAttribute(
            "salary_structure.created_by"
        )

    name = factory.Sequence(
            lambda n: f"Rule {n}"
        )

    is_active = True
    
    
class SalaryRuleVersionFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = SalaryRuleVersion

    rule = factory.SubFactory(
        SalaryRuleFactory
    )

    company = factory.SelfAttribute(
        "rule.company"
    )

    created_by = factory.SelfAttribute(
        "rule.created_by"
    )

    version = 1

    sequence = 1

    formula = "1000"

    condition = ""

    is_active = True