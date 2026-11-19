# apps/payroll/services/rule_versioning_service.py

from django.db import transaction
from apps.payroll.models import SalaryRuleVersion


from django.db import transaction

from apps.payroll.models import SalaryRuleVersion
from core.services.audit_service import AuditService


class RuleVersioningService:

    @staticmethod
    @transaction.atomic
    def create_new_version(rule, data, user):

        last_version = rule.versions.order_by("-version").first()
        new_version_number = 1 if not last_version else last_version.version + 1

        # deactivate old versions
        rule.versions.update(is_active=False)

        new_version = SalaryRuleVersion.objects.create(
            rule=rule,
            version=new_version_number,
            sequence=data["sequence"],
            condition=data.get("condition", ""),
            formula=data["formula"],
            is_active=True,
            created_by=user
        )

        # 🔥 ADD IT HERE (after successful creation)
        AuditService.log(
            model_instance=rule,
            action="UPDATE",
            user=user,
            old_data={
                "formula": last_version.formula if last_version else None
            },
            new_data={
                "formula": data["formula"]
            },
            description=f"Rule updated to version {new_version_number}"
        )

        return new_version