# apps/workflow/services/approval_engine.py

from django.db import transaction
from django.core.exceptions import ValidationError


class ApprovalEngine:
    """
    ERP Workflow Engine for document approvals

    Supports:
    - Purchase Orders
    - Supplier Invoices
    - Extensible to other modules
    """

    # =====================================================
    # START APPROVAL PROCESS
    # =====================================================
    @staticmethod
    @transaction.atomic
    def submit_for_approval(document, user):
        """
        Moves document from Draft → Pending Approval
        """

        if document.status != "draft":
            raise ValidationError("Only draft documents can be submitted.")

        document.status = "pending_approval"
        document.submitted_by = user
        document.save(update_fields=["status", "submitted_by"])

        ApprovalEngine._create_initial_task(document)

        return document

    # =====================================================
    # APPROVE STEP
    # =====================================================
    @staticmethod
    @transaction.atomic
    def approve(document, user, comment=None):
        """
        Approve a document step-by-step
        """

        if document.status != "pending_approval":
            raise ValidationError("Document is not in approval state.")

        current_step = ApprovalEngine._get_current_step(document)

        if not ApprovalEngine._user_can_approve(current_step, user):
            raise ValidationError("User not authorized for this step.")

        ApprovalEngine._mark_step_approved(current_step, user, comment)

        # Check if more steps exist
        if ApprovalEngine._has_next_step(document):
            ApprovalEngine._move_to_next_step(document)
        else:
            document.status = "approved"
            document.save(update_fields=["status"])

        return document

    # =====================================================
    # REJECT DOCUMENT
    # =====================================================
    @staticmethod
    @transaction.atomic
    def reject(document, user, reason):
        """
        Reject document and stop workflow
        """

        if document.status not in ["pending_approval"]:
            raise ValidationError("Only pending documents can be rejected.")

        document.status = "rejected"
        document.rejection_reason = reason
        document.rejected_by = user
        document.save(update_fields=["status", "rejection_reason", "rejected_by"])

        ApprovalEngine._close_all_tasks(document)

        return document

    # =====================================================
    # INTERNAL WORKFLOW METHODS
    # =====================================================

    @staticmethod
    def _create_initial_task(document):
        """
        Create first approval step
        """
        # In real ERP: create ApprovalTask model
        pass

    @staticmethod
    def _get_current_step(document):
        """
        Fetch active approval step
        """
        return None

    @staticmethod
    def _user_can_approve(step, user):
        """
        Role/permission validation
        """
        return True  # replace with RBAC later

    @staticmethod
    def _mark_step_approved(step, user, comment):
        """
        Mark approval step as done
        """
        pass

    @staticmethod
    def _has_next_step(document):
        """
        Check if more approval levels exist
        """
        return False

    @staticmethod
    def _move_to_next_step(document):
        """
        Advance workflow step
        """
        pass

    @staticmethod
    def _close_all_tasks(document):
        """
        Close pending workflow tasks after rejection
        """
        pass