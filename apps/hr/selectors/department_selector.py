# apps/hr/selectors/department_selector.py

from apps.hr.models import Department


class DepartmentSelector:

    @staticmethod
    def get_company_departments(company):
        return Department.objects.filter(company=company)