# apps/finance/models/audit_log.py

from django.db import models

class AuditLog(models.Model):

    ACTIONS = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("POST", "Post"),
    ]

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True
    )

    action = models.CharField(max_length=10, choices=ACTIONS)

    model_name = models.CharField(max_length=100)

    object_id = models.IntegerField()

    timestamp = models.DateTimeField(auto_now_add=True)

    description = models.TextField(null=True, blank=True)