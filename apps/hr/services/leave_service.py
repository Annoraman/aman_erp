# apps/hr/services/leave_service.py

from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.payroll.models import payroll_run
from core.services.audit_service import AuditService


class LeaveService:

    @staticmethod
    def submit(leave_request):

        if leave_request.status != "DRAFT":
            raise ValidationError("Only DRAFT can be submitted")

        leave_request.status = "SUBMITTED"
        leave_request.save()

    @staticmethod
    def approve(leave_request, user):

        if leave_request.status != "SUBMITTED":
            raise ValidationError("Only SUBMITTED can be approved")

        leave_request.status = "APPROVED"
        leave_request.approved_by = user
        leave_request.approved_at = timezone.now()
        leave_request.save()

        AuditService.log(
                model_instance=payroll_run,
                action="APPROVE",
                user=user,
                old_data={"status": old_status},
                new_data={"status": "APPROVED"},
                description="Payroll approved"
            )

    @staticmethod
    def reject(leave_request, user):

        if leave_request.status != "SUBMITTED":
            raise ValidationError("Only SUBMITTED can be rejected")

        leave_request.status = "REJECTED"
        leave_request.approved_by = user
        leave_request.approved_at = timezone.now()
        leave_request.save()