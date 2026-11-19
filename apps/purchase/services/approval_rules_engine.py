# apps/workflow/services/approval_rules_engine.py

from decimal import Decimal
from django.core.exceptions import ValidationError

from apps.workflow.models import ApprovalRule


class ApprovalRulesEngine:
    """
    ERP Dynamic Approval Rules Engine

    Determines:
    - Required approval steps
    - Approval hierarchy
    - Conditional routing logic
    """

    # =====================================================
    # MAIN ENTRY POINT
    # =====================================================
    @staticmethod
    def build_workflow(document):
        """
        Returns ordered list of approval steps
        """

        rules = ApprovalRule.objects.filter(
            company=document.company,
            document_type=document.__class__.__name__,
            is_active=True
        ).order_by("priority")

        if not rules.exists():
            raise ValidationError("No approval rules defined for this document.")

        steps = []

        for rule in rules:
            if ApprovalRulesEngine._evaluate_rule(rule, document):
                steps.append({
                    "role": rule.role,
                    "min_amount": rule.min_amount,
                    "max_amount": rule.max_amount,
                    "sequence": rule.sequence
                })

        # Ensure at least one step
        if not steps:
            raise ValidationError("No valid approval steps generated.")

        return sorted(steps, key=lambda x: x["sequence"])

    # =====================================================
    # RULE EVALUATION CORE
    # =====================================================
    @staticmethod
    def _evaluate_rule(rule, document):
        """
        Checks if rule applies to document
        """

        amount = getattr(document, "total_amount", Decimal("0.00"))

        # -------------------------
        # Amount range check
        # -------------------------
        if rule.min_amount and amount < rule.min_amount:
            return False

        if rule.max_amount and amount > rule.max_amount:
            return False

        # -------------------------
        # Supplier condition (optional)
        # -------------------------
        if rule.only_high_risk_supplier:
            if not getattr(document.supplier, "risk_level", None) == "high":
                return False

        # -------------------------
        # Department condition (optional)
        # -------------------------
        if rule.department:
            if getattr(document, "department_id", None) != rule.department_id:
                return False

        return True