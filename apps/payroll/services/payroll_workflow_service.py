from django.utils import timezone

from apps.payroll.services.payroll_posting_service import PayrollPostingService


class PayrollWorkflowService:

    @staticmethod
    def submit_for_review(payroll_run):

        if payroll_run.status != "DRAFT":
            raise Exception("Only DRAFT payroll can be submitted")

        payroll_run.status = "REVIEW"
        payroll_run.save()

    @staticmethod
    def approve(payroll_run, user):

        if payroll_run.status != "REVIEW":
            raise Exception("Only REVIEW payroll can be approved")

        payroll_run.status = "APPROVED"
        payroll_run.approved_by = user
        payroll_run.approved_at = timezone.now()
        payroll_run.save()

    @staticmethod
    def post(payroll_run):

        if payroll_run.status != "APPROVED":
            raise Exception("Only APPROVED payroll can be posted")

        # post to accounting
        PayrollPostingService.post(payroll_run)

        payroll_run.status = "POSTED"
        payroll_run.posted_at = timezone.now()
        payroll_run.save()