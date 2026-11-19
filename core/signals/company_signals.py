#core/signals/company_signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models.company import Company
from apps.accounts.config import RBACBootstrapService

@receiver(post_save, sender=Company)
def create_company_rbac(sender, instance, created, **kwargs):
    if created:
        RBACBootstrapService.initialize_company(instance)
