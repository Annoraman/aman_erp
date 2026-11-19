from apps.hr.services.attendance_service import AttendanceService
from apps.payroll.domain.payroll_engine import PayrollEngine
from apps.payroll.domain.simulation_context import PayrollSimulationContext


class PayrollSimulationEngine:

    @staticmethod
    def simulate(contract, period_start, period_end, overrides=None):

        employee = contract.employee

        # -------------------------
        # Infrastructure call
        # -------------------------
        attendance = AttendanceService.summarize(
            employee,
            period_start,
            period_end
        )

        # -------------------------
        # Build domain context (VO)
        # -------------------------
        context = PayrollSimulationContext.from_sources(
            contract,
            attendance,
            overrides
        )

        # -------------------------
        # Pure domain execution
        # -------------------------
        return PayrollEngine.generate(
            contract=contract,
            period_start=period_start,
            period_end=period_end,
            extra_context=context
        )