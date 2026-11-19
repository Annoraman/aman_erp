# apps/payroll/selectors/payslip_selector.py

from apps.payroll.models import Payslip

class PayslipSelector:

    @staticmethod
    def get_employee_payslips(employee):
        return Payslip.objects.filter(employee=employee)

    @staticmethod
    def get_payslip_with_lines(payslip_id):
        return Payslip.objects.prefetch_related("lines").get(id=payslip_id)