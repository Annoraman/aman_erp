# apps/payroll/reports/payslip_report.py

from io import BytesIO
from reportlab.pdfgen import canvas

class PayslipReport:

    @staticmethod
    def generate(payslip):

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)

        pdf.setFont("Helvetica", 12)

        # Header
        pdf.drawString(50, 800, f"Payslip - {payslip.employee}")

        pdf.drawString(50, 780, f"Period: {payslip.period_start} - {payslip.period_end}")

        y = 740

        # Lines
        for line in payslip.lines.all():
            pdf.drawString(
                50,
                y,
                f"{line.component.name} : {line.amount}"
            )
            y -= 20

        # Summary
        pdf.drawString(50, y - 20, f"Gross: {payslip.gross_salary}")
        pdf.drawString(50, y - 40, f"Net: {payslip.net_salary}")

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        return buffer