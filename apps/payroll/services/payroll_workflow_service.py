# apps/payroll/services/payroll_workflow_service.py

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.payroll.services.payroll_posting_service import PayrollPostingService


class PayrollWorkflowService:

    @staticmethod
    @transaction.atomic
    def submit_for_review(payroll_run):

        if payroll_run.status != "DRAFT":
            raise ValidationError("Only DRAFT payroll can be submitted.")

        if not payroll_run.payslips.exists():
            raise ValidationError("Cannot submit payroll without payslips.")

        payroll_run.status = "REVIEW"
        payroll_run.submitted_at = timezone.now()
        payroll_run.save(update_fields=["status", "submitted_at"])

    @staticmethod
    @transaction.atomic
    def approve(payroll_run, user):

        if payroll_run.status != "REVIEW":
            raise ValidationError("Only REVIEW payroll can be approved.")

        payroll_run.status = "APPROVED"
        payroll_run.approved_by = user
        payroll_run.approved_at = timezone.now()
        payroll_run.save(update_fields=["status", "approved_by", "approved_at"])

    @staticmethod
    @transaction.atomic
    def post(payroll_run):

        if payroll_run.status == "POSTED":
            raise Exception("Already posted")

        if payroll_run.status != "APPROVED":
            raise ValidationError("Only APPROVED payroll can be posted.")

        if payroll_run.status == "POSTED":
            raise ValidationError("Payroll already posted.")

        if not payroll_run.payslips.exists():
            raise ValidationError("No payslips to post.")

        # 🔥 Lock rows (important in real systems)
        payslips = payroll_run.payslips.select_for_update()

        # 🔥 Post to finance
        PayrollPostingService.post(payroll_run)

        payroll_run.status = "POSTED"
        payroll_run.posted_at = timezone.now()
        payroll_run.save(update_fields=["status", "posted_at"])