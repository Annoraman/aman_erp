from decimal import Decimal

from apps.payroll.models import Payslip, PayslipLine, SalaryComponent
from apps.hr.selectors.employee_selector import EmployeeSelector


class PayrollEngine:

    @staticmethod
    
    def run(payroll_run):
        if payroll_run.status != "DRAFT":
                raise Exception("Payroll can only be processed in DRAFT state")
        employees = EmployeeSelector.get_active_employees()

        for employee in employees:

            contract = EmployeeSelector.get_active_contract(employee)

            if not contract:
                continue

            PayrollEngine._process_employee(employee, contract, payroll_run)

    @staticmethod
    def _process_employee(employee, contract, payroll_run):

        if not contract.salary_structure:
            return

        basic_salary = contract.salary
        components = contract.salary_structure.components.all()

        allowances = Decimal("0.00")
        deductions = Decimal("0.00")

        payslip = Payslip.objects.create(
            employee=employee,
            payroll_run=payroll_run,
            basic_salary=basic_salary,
            gross_salary=0,
            net_salary=0,
        )

        # Basic line
        PayslipLine.objects.create(
            payslip=payslip,
            component_name="Basic Salary",
            component_type=PayslipLine.ALLOWANCE,
            amount=basic_salary,
        )

        for component in components:

            amount = PayrollEngine._calculate_component(component, basic_salary)

            PayslipLine.objects.create(
                payslip=payslip,
                component_name=component.name,
                component_type=component.component_type,
                amount=amount,
                account=component.account
            )

            if component.component_type == SalaryComponent.ALLOWANCE:
                allowances += amount
            else:
                deductions += amount

        gross_salary = basic_salary + allowances
        net_salary = gross_salary - deductions

        payslip.gross_salary = gross_salary
        payslip.net_salary = net_salary
        payslip.save()

    @staticmethod
    def _calculate_component(component, basic_salary):

        if component.calculation_type == SalaryComponent.FIXED:
            return component.value

        elif component.calculation_type == SalaryComponent.PERCENTAGE:
            return (component.value / Decimal("100")) * basic_salary

        return Decimal("0.00")