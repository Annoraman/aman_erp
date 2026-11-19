from django.contrib import admin
from apps.payroll.models.payroll_period import PayrollPeriod
from apps.payroll.models.payslip import Payslip
from apps.payroll.models.salary_component import SalaryComponent
from apps.payroll.models.salary_structure import SalaryStructure
from apps.payroll.models.salary_rule import SalaryRule
from apps.payroll.models.salary_rule_version import SalaryRuleVersion

# Register your models here.
@admin.register(PayrollPeriod)
class ContractAdmin(admin.ModelAdmin):
    pass

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    pass

@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    pass

@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    pass


@admin.register(SalaryRule)
class SalaryRuleAdmin(admin.ModelAdmin):
    pass

@admin.register(SalaryRuleVersion)
class SalaryRuleVersionAdmin(admin.ModelAdmin):
    pass


