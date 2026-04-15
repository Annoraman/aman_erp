# apps/finance/services/audit_service.py

from apps.finance.models import AuditLog

class AuditService:

    @staticmethod
    def log(user, action, instance, description=""):

        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=instance.__class__.__name__,
            object_id=instance.id,
            description=description
        )