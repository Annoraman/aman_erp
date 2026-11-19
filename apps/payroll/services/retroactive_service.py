# apps/payroll/services/retroactive_payroll_service.py

from django.db import transaction

from apps.payroll.domain.retroactive_payroll_engine import (
    RetroactivePayrollEngine
)

from apps.payroll.models import PayrollAdjustment


class RetroactivePayrollService:

    @staticmethod
    @transaction.atomic
    def process(old_payslip, new_result):

        # -----------------------------------
        # CALCULATE DIFFERENCES
        # -----------------------------------
        retro_result = (
            RetroactivePayrollEngine.calculate_differences(
                old_payslip=old_payslip,
                new_result=new_result
            )
        )

        adjustments = []

        # -----------------------------------
        # CREATE ADJUSTMENTS
        # -----------------------------------
        for item in retro_result["differences"]:

            adjustment = PayrollAdjustment.objects.create(
                employee=old_payslip.employee,

                component=item["component"],

                amount=item["difference"],

                payroll_period=old_payslip.payroll_period,

                notes=(
                    f"Retroactive adjustment "
                    f"for {item['code']}"
                )
            )

            adjustments.append(adjustment)

        return {
            "adjustments": adjustments,
            "total_difference":
                retro_result["total_difference"],
        }