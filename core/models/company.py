# E:\aman_erp\backend\core\models\company.py

from django.db import models
from core.models.base import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
#from apps.accounts.services.rbac_bootstrap import RBACBootstrapService

class Company(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]
    """
    @receiver(post_save, sender=Company)
    def create_company_rbac(sender, instance, created, **kwargs):
        if created:
            RBACBootstrapService.initialize_company(instance)
    """

    def __str__(self):
        return self.name
        



