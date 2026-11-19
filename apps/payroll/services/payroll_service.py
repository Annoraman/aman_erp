# apps/payroll/services/payroll_generation_service.py

import logging
from decimal import Decimal
from typing import Optional, Dict, Any

from django.db import transaction
from django.core.exceptions import ValidationError

from apps.hr.models import Contract
from apps.payroll.models import (
    PayrollRun,
    Payslip,
    PayslipLine,
)
from apps.payroll.domain.payroll_engine import PayrollEngine

logger = logging.getLogger(__name__)

class PayrollGenerationService:

    @staticmethod
    @transaction.atomic
    def generate(
        payroll_run: PayrollRun,
        extra_context: Optional[Dict[str, Any]] = None,
        enable_debug: bool = False,
        default_proration_factor: Optional[Decimal] = None,
    ) -> PayrollRun:

        # =====================================================
        # VALIDATION LAYER
        # =====================================================
        if payroll_run.status != PayrollRun.DRAFT:
            raise ValidationError(
                "Only DRAFT payroll runs can be generated."
            )

        if payroll_run.payslips.exists():
            raise ValidationError(
                "Payroll already generated for this run."
            )

        # =====================================================
        # LOAD CONTRACTS
        # =====================================================
        contracts = (
            Contract.objects
            .filter(
                company=payroll_run.company,
                is_active=True,
                salary_structure__isnull=False,
                salary_structure__is_active=True,
            )
            .select_related(
                "employee",
                "salary_structure",
            )
        )

        if not contracts.exists():
            raise ValidationError(
                "No valid active contracts found for payroll generation."
            )

        logger.info(
            "Payroll generation started",
            extra={
                "payroll_run_id": payroll_run.id,
                "company_id": payroll_run.company_id,
                "contracts_count": contracts.count(),
            }
        )

        # =====================================================
        # EXECUTION LAYER
        # =====================================================
        try:
            for contract in contracts:

                if not contract.employee:
                    raise ValidationError(
                        f"Invalid contract {contract.id}: missing employee."
                    )

                proration_factor = (
                    PayrollGenerationService._get_proration_factor(
                        contract=contract,
                        period=payroll_run.period,
                        default_factor=default_proration_factor,
                    )
                )

                PayrollGenerationService._generate_payslip(
                    payroll_run=payroll_run,
                    contract=contract,
                    extra_context=extra_context,
                    enable_debug=enable_debug,
                    proration_factor=proration_factor,
                )

        except Exception as exc:

            logger.exception(
                "Payroll generation failed",
                extra={
                    "payroll_run_id": payroll_run.id,
                    "company_id": payroll_run.company_id,
                }
            )

            payroll_run.failure_reason = (
                f"PayrollRun={payroll_run.id} | Error={str(exc)}"
            )
            payroll_run.save(update_fields=["failure_reason"])

            print("\nREAL ERROR =", repr(exc))
            raise ValidationError(
                "Payroll generation failed. Check logs for details."
            ) from exc

        # clear failure state on success
        payroll_run.failure_reason = None
        payroll_run.save(update_fields=["failure_reason"])

        logger.info(
            "Payroll generation completed successfully",
            extra={
                "payroll_run_id": payroll_run.id,
            }
        )

        return payroll_run

    # =========================================================
    # PAYSLIP GENERATION
    # =========================================================
    @staticmethod
    def _generate_payslip(
        payroll_run: PayrollRun,
        contract: Contract,
        extra_context: Optional[Dict[str, Any]],
        enable_debug: bool,
        proration_factor: Optional[Decimal],
    ) -> Payslip:

        # -----------------------------------------
        # ENGINE EXECUTION
        # -----------------------------------------
        result = PayrollEngine.generate(
            contract=contract,
            period=payroll_run.period,
            extra_context=extra_context,
            enable_debug=enable_debug,
            proration_factor=proration_factor,
        )

        # -----------------------------------------
        # PAYSLIP HEADER
        # -----------------------------------------
        payslip = Payslip.objects.create(
            company=payroll_run.company,
            payroll_run=payroll_run,
            period=payroll_run.period,
            employee=contract.employee,
            contract=contract,

            gross_salary=result["gross"],
            deductions=result["deductions"],
            net_salary=result["net"],

            taxable_gross=result["taxable_gross"],
            pensionable_gross=result["pensionable_gross"],
            insurable_gross=result["insurable_gross"],
        )

        # -----------------------------------------
        # PAYSLIP LINES
        # -----------------------------------------
        lines = []

        for line in result["lines"]:

            lines.append(
                PayslipLine(
                    company=payroll_run.company,
                    payslip=payslip,

                    component_id=line["component_id"],
                    component_code=line["component_code"],
                    component_name=line["component_name"],
                    component_type=line["type"],

                    amount=line["amount"],
                    sequence=line["sequence"],

                    rule_version_id=line["rule_version_id"],

                    formula_snapshot=line.get("formula_snapshot"),
                    condition_snapshot=line.get("condition_snapshot"),
                )
            )

        if lines:
            PayslipLine.objects.bulk_create(
                lines,
                batch_size=500
            )

        # -----------------------------------------
        # DEBUG INFO
        # -----------------------------------------
        if enable_debug and "debug_trace" in result:

            payslip.debug_info = {
                "trace": result["debug_trace"],
                "errors": result.get("errors", []),
                "contract_id": contract.id,
                "employee_id": contract.employee_id,
            }

            payslip.save(update_fields=["debug_info"])

        return payslip

    # =========================================================
    # PRORATION HOOK (FUTURE)
    # =========================================================
    @staticmethod
    def _get_proration_factor(
        contract: Contract,
        period,
        default_factor: Optional[Decimal],
    ) -> Optional[Decimal]:

        """
        Future enhancements:
        - Mid-month joiners
        - Termination during period
        - Unpaid leave
        - Suspension
        """

        return default_factor