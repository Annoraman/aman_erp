# apps/hr/selectors/employee_selector.py

from apps.hr.models import Employee


class EmployeeSelector:

    @staticmethod
    def get_active_employees():
        return Employee.objects.filter(status="ACTIVE")

    @staticmethod
    def get_active_contract(employee):
        return employee.contracts.filter(status="ACTIVE").first()