# apps/payroll/api/views.py

from django.http import HttpResponse
from apps.payroll.models.payslip import Payslip
from apps.payroll.reports.payslip_report import PayslipReport


def download_payslip(request, payslip_id):

    payslip = Payslip.objects.get(id=payslip_id)

    pdf = PayslipReport.generate(payslip)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=payslip.pdf"

    return response