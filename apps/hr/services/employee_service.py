# apps/hr/services/employee_service.py

from django.db import transaction
from apps.hr.models import Employee, Contract


class EmployeeService:

    @staticmethod
    @transaction.atomic
    def create_employee(data, contract_data):

        employee = Employee.objects.create(**data)

        Contract.objects.create(
            employee=employee,
            **contract_data
        )

        return employee

    @staticmethod
    def assign_department(employee, department):
        employee.department = department
        employee.save(update_fields=["department"])

    @staticmethod
    def assign_manager(employee, manager):
        employee.manager = manager
        employee.save(update_fields=["manager"])

    @staticmethod
    @transaction.atomic
    def terminate_employee(employee):

        employee.status = Employee.INACTIVE
        employee.save(update_fields=["status"])

        employee.contracts.filter(status="ACTIVE").update(status="TERMINATED")