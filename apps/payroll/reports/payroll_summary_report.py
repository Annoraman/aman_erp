# apps/payroll/reports/payroll_summary_report.py

class PayrollSummaryReport:

    @staticmethod
    def generate(payroll_run):

        payslips = payroll_run.payslips.all()

        total_gross = sum(p.gross_salary for p in payslips)
        total_net = sum(p.net_salary for p in payslips)

        total_employees = payslips.count()

        return {
            "total_employees": total_employees,
            "total_gross": total_gross,
            "total_net": total_net,
        }