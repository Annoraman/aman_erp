from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PayrollSimulationContext:
    basic_salary: Decimal
    absent_days: int
    late_days: int
    worked_hours: Decimal

    @staticmethod
    def from_sources(contract, attendance, overrides=None):

        overrides = overrides or {}

        return PayrollSimulationContext(
            basic_salary=overrides.get("salary", contract.basic_salary),
            absent_days=overrides.get("absent_days", attendance["absent_days"]),
            late_days=overrides.get("late_days", attendance["late_days"]),
            worked_hours=overrides.get("worked_hours", attendance["total_hours"]),
        )