# apps/core/services/audit_service.py

from core.models.audit_log import AuditLog


class AuditService:

    @staticmethod
    def log(model_instance, action, user=None, old_data=None, new_data=None, description=""):

        AuditLog.objects.create(
            model_name=model_instance.__class__.__name__,
            object_id=str(model_instance.id),
            action=action,
            user=user,
            old_data=old_data,
            new_data=new_data,
            description=description
        )