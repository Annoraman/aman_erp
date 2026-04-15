# apps/hr/services/department_service.py

from apps.hr.models import Department


class DepartmentService:

    @staticmethod
    def create_department(**data):
        return Department.objects.create(**data)