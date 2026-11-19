# apps/payroll/domain/payroll_engine.py

import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Any, Optional, Tuple, Set

from django.core.exceptions import ValidationError

from apps.hr.services.attendance_service import AttendanceService
from apps.payroll.domain.rules_engine import RulesEngine
from apps.payroll.models import (
    SalaryRuleVersion,
    salary_scale,
)

logger = logging.getLogger(__name__)

class PayrollEngine:
    """
    Enterprise Payroll Engine

    Features:
    - Safe rule execution
    - Runtime chaining
    - Taxable/Pensionable accumulators
    - Debug tracing
    - Formula snapshots
    - Circular dependency protection
    - Decimal normalization
    - Production logging
    - ERP-grade totals
    """

    DECIMAL_PLACES = Decimal("0.01")

    # =====================================
    # MAIN ENTRY
    # =====================================
    @staticmethod
    def generate(
        contract,
        period,
        extra_context: Optional[Dict[str, Any]] = None,
        enable_debug: bool = False,
        proration_factor: Optional[Decimal] = None,
        freeze_check: bool = True,
    ) -> Dict[str, Any]:

        # ---------------------------------
        # PAYROLL FREEZE PROTECTION
        # ---------------------------------
        if freeze_check:

            existing_posted = (
                contract.payslip_set
                .filter(
                    period=period,
                    status="POSTED"
                )
                .exists()
            )

            if existing_posted:
                raise ValidationError(
                    "Cannot regenerate POSTED payroll."
                )

        employee = contract.employee
        structure = contract.salary_structure

        # ---------------------------------
        # LOAD ACTIVE RULES
        # ---------------------------------
        rules = (
            SalaryRuleVersion.objects
            .filter(
                rule__salary_structure=structure,
                is_active=True
            )
            .select_related(
                "rule",
                "rule__component"
            )
            .order_by("sequence", "id")
        )

        if not rules.exists():
            raise ValidationError(
                "No active salary rules found."
            )

        # ---------------------------------
        # DUPLICATE COMPONENT PROTECTION
        # ---------------------------------
        PayrollEngine._validate_duplicate_components(
            rules
        )

        # ---------------------------------
        # ATTENDANCE
        # ---------------------------------
        attendance = AttendanceService.summarize(
            employee=employee,
            start= period.start_date,
            end= period.end_date
        )

        # ---------------------------------
        # CONTEXT BUILD
        # ---------------------------------
        context = PayrollEngine._build_context(
            contract=contract,
            employee=employee,
            attendance=attendance,
            extra_context=extra_context,
            proration_factor=proration_factor
        )

        # ---------------------------------
        # RUNTIME TOTALS
        # ---------------------------------
        totals = PayrollEngine._initialize_totals()

        # ---------------------------------
        # RESULTS
        # ---------------------------------
        lines: List[Dict[str, Any]] = []

        debug_trace: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []

        executed_codes: Set[str] = set()

        # =====================================
        # RULE EXECUTION LOOP
        # =====================================
        for rule_version in rules:

            line, error, trace = PayrollEngine._execute_rule(
                contract,
                rule_version=rule_version,
                context=context,
                executed_codes=executed_codes,
                enable_debug=enable_debug
            )

            # ---------------------------------
            # RULE ERROR
            # ---------------------------------
            if error:

                errors.append(error)

                if enable_debug and trace:
                    debug_trace.append(trace)

                continue

            # ---------------------------------
            # CONDITION FALSE
            # ---------------------------------
            if line is None:
                continue

            lines.append(line)

            if enable_debug and trace:
                debug_trace.append(trace)

            # ---------------------------------
            # UPDATE TOTALS
            # ---------------------------------
            PayrollEngine._update_totals(
                totals=totals,
                line=line
            )

            # ---------------------------------
            # UPDATE CONTEXT
            # ---------------------------------
            PayrollEngine._update_runtime_context(
                context=context,
                totals=totals
            )

        # =====================================
        # FINAL RESULT
        # =====================================
        result = {
            "lines": lines,

            "gross": totals["gross"],
            "deductions": totals["deductions"],
            "net": totals["net"],

            "taxable_gross": totals["taxable_gross"],
            "pensionable_gross": totals["pensionable_gross"],
            "insurable_gross": totals["insurable_gross"],
        }

        if enable_debug:

            result["debug_trace"] = debug_trace
            result["errors"] = errors

        return result

    # =====================================
    # RULE EXECUTION
    # =====================================
    @staticmethod
    def _execute_rule(
        contract,
        rule_version,
        context: Dict[str, Any],
        executed_codes: Set[str],
        enable_debug: bool = False
        
    ) -> Tuple[
        Optional[Dict[str, Any]],
        Optional[Dict[str, Any]],
        Optional[Dict[str, Any]]
    ]:

        try:

            component = rule_version.rule.component
            code = component.code

            # ---------------------------------
            # CIRCULAR / DUPLICATE EXECUTION
            # ---------------------------------
            if code in executed_codes:

                raise ValidationError(
                    f"Duplicate/circular component detected: {code}"
                )

            # ---------------------------------
            # CONDITION
            # ---------------------------------
            if not PayrollEngine._check_condition(
                rule_version,
                context
            ):
                return None, None, None

            # ---------------------------------
            # FORMULA
            # ---------------------------------
            if code == "BASIC":
                if contract.basic_salary > Decimal('0.00') :
                    amount = Decimal(str(contract.basic_salary))
                else:
                    amount = PayrollEngine._evaluate(
                    rule_version,
                    context
                    )
            else:        
                amount = PayrollEngine._evaluate(
                    rule_version,
                    context
                )

            # ---------------------------------
            # QUANTIZE
            # ---------------------------------
            amount = PayrollEngine._quantize(amount)

            # ---------------------------------
            # RULE CHAINING
            # ---------------------------------
            context[code] = amount

            executed_codes.add(code)

            # ---------------------------------
            # BUILD LINE
            # ---------------------------------
            line = {

                # component
                "component_id": component.id,
                "component_code": code,
                "component_name": component.name,

                # amount
                "amount": amount,

                # classifications
                "type": component.component_type,

                "is_taxable": component.is_taxable,
                "is_pensionable": component.is_pensionable,
                "is_insurable": component.is_insurable,

                # snapshots
                "rule_version_id": rule_version.id,
                "formula_snapshot": rule_version.formula,
                "condition_snapshot": rule_version.condition,

                # metadata
                "sequence": rule_version.sequence,
            }

            trace = None

            if enable_debug:

                trace = {
                    "rule": code,
                    "formula": rule_version.formula,
                    "result": str(amount)
                }

            return line, None, trace

        except Exception as e:

            error_info = {

                "rule_id": rule_version.id,

                "rule_code": getattr(
                    rule_version.rule.component,
                    "code",
                    "UNKNOWN"
                ),

                "error": str(e)
            }

            logger.exception(
                f"Payroll rule execution failed: {error_info}"
            )

            trace = None

            if enable_debug:

                trace = {
                    "rule": error_info["rule_code"],
                    "error": str(e)
                }

            return None, error_info, trace

    # =====================================
    # CONTEXT BUILDER
    # =====================================
    @staticmethod
    def _build_context(
        contract,
        employee,
        attendance: Dict[str, Any],
        extra_context: Optional[Dict[str, Any]] = None,
        proration_factor: Optional[Decimal] = None
    ) -> Dict[str, Any]:

        basic_salary = Decimal(contract.basic_salary)

        # ---------------------------------
        # SALARY SCALE OVERRIDE
        # ---------------------------------
        if employee.job_grade and employee.grade_step:

            scale_value = (
                salary_scale.SalaryScale.objects
                .filter(
                    job_grade=employee.job_grade,
                    grade_step=employee.grade_step,
                    component__code="BASIC"
                )
                .values_list("value", flat=True)
                .first()
            )

            if scale_value is not None:
                basic_salary = Decimal(scale_value)

        # ---------------------------------
        # PRORATION
        # ---------------------------------
        if proration_factor is not None:

            basic_salary *= Decimal(
                str(proration_factor)
            )

        basic_salary = PayrollEngine._quantize(
            basic_salary
        )

        context = {

            # objects
            "contract": contract,
            "employee": employee,

            # salary
            "BASIC": basic_salary,

            # attendance
            "absent_days": Decimal(
                attendance.get("absent_days", 0)
            ),

            "late_days": Decimal(
                attendance.get("late_days", 0)
            ),

            "worked_hours": Decimal(
                attendance.get("total_hours", 0)
            ),

            "leave_days": Decimal(
                attendance.get("leave_days", 0)
            ),

            # accumulators
            "GROSS": Decimal("0.00"),
            "DEDUCTIONS": Decimal("0.00"),
            "NET": Decimal("0.00"),

            "TAXABLE_GROSS": Decimal("0.00"),
            "PENSIONABLE_GROSS": Decimal("0.00"),
            "INSURABLE_GROSS": Decimal("0.00"),

            # proration
            "proration_factor": (
                Decimal(str(proration_factor))
                if proration_factor is not None
                else Decimal("1.00")
            ),
        }

        # ---------------------------------
        # EXTRA CONTEXT
        # ---------------------------------
        if extra_context:

            for k, v in extra_context.items():

                if isinstance(v, Decimal):

                    context[k] = v

                elif isinstance(v, (int, float, str)):

                    context[k] = Decimal(str(v))

                else:

                    context[k] = v

        return context

    # =====================================
    # CONDITION
    # =====================================
    @staticmethod
    def _check_condition(
        rule_version,
        context: Dict[str, Any]
    ) -> bool:

        if not rule_version.condition:
            return True

        try:

            result = RulesEngine.evaluate(
                rule_version.condition,
                context
            )

            return bool(result)

        except Exception as e:

            logger.warning(
                f"[CONDITION ERROR] "
                f"rule={rule_version.id}: {e}"
            )

            return False

    # =====================================
    # FORMULA
    # =====================================
    @staticmethod
    def _evaluate(
        rule_version,
        context: Dict[str, Any]
    ) -> Decimal:

        try:

            result = RulesEngine.evaluate(
                rule_version.formula,
                context
            )

            if result is None:
                return Decimal("0.00")

            return Decimal(str(result))

        except Exception as e:

            logger.error(
                f"[FORMULA ERROR] "
                f"rule={rule_version.id}: {e}"
            )

            return Decimal("0.00")

    # =====================================
    # UPDATE TOTALS
    # =====================================
    @staticmethod
    def _update_totals(
        totals: Dict[str, Decimal],
        line: Dict[str, Any]
    ) -> None:

        amount = Decimal(line["amount"])

        if line["type"] == "EARNING":

            totals["gross"] += amount

            if line.get("is_taxable"):
                totals["taxable_gross"] += amount

            if line.get("is_pensionable"):
                totals["pensionable_gross"] += amount

            if line.get("is_insurable"):
                totals["insurable_gross"] += amount

        else:

            totals["deductions"] += amount

        totals["net"] = (
            totals["gross"]
            - totals["deductions"]
        )

        # normalize
        for key in totals:
            totals[key] = PayrollEngine._quantize(
                totals[key]
            )

    # =====================================
    # UPDATE RUNTIME CONTEXT
    # =====================================
    @staticmethod
    def _update_runtime_context(
        context: Dict[str, Any],
        totals: Dict[str, Decimal]
    ) -> None:

        context["GROSS"] = totals["gross"]
        context["DEDUCTIONS"] = totals["deductions"]
        context["NET"] = totals["net"]

        context["TAXABLE_GROSS"] = totals["taxable_gross"]

        context["PENSIONABLE_GROSS"] = (
            totals["pensionable_gross"]
        )

        context["INSURABLE_GROSS"] = (
            totals["insurable_gross"]
        )

    # =====================================
    # INITIALIZE TOTALS
    # =====================================
    @staticmethod
    def _initialize_totals() -> Dict[str, Decimal]:

        return {

            "gross": Decimal("0.00"),
            "deductions": Decimal("0.00"),
            "net": Decimal("0.00"),

            "taxable_gross": Decimal("0.00"),

            "pensionable_gross": Decimal("0.00"),

            "insurable_gross": Decimal("0.00"),
        }

    # =====================================
    # DUPLICATE COMPONENT PROTECTION
    # =====================================
    @staticmethod
    def _validate_duplicate_components(
        rules
    ) -> None:

        seen = set()

        for rule in rules:

            code = rule.rule.component.code

            if code in seen:

                raise ValidationError(
                    f"Duplicate component code found: {code}"
                )

            seen.add(code)

    # =====================================
    # QUANTIZE DECIMAL
    # =====================================
    @staticmethod
    def _quantize(value: Decimal) -> Decimal:

        return Decimal(value).quantize(
            PayrollEngine.DECIMAL_PLACES,
            rounding=ROUND_HALF_UP
        )

    # =====================================
    # EXTERNAL UTILITY
    # =====================================
    @staticmethod
    def compute_totals_from_lines(
        lines: List[Dict[str, Any]]
    ) -> Dict[str, Decimal]:

        totals = PayrollEngine._initialize_totals()

        for line in lines:

            PayrollEngine._update_totals(
                totals=totals,
                line=line
            )

        return totals