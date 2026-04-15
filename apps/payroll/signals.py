# apps/payroll/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.payroll.models import Payslip
from apps.finance.integrations.payroll_integration import PayrollAccountingIntegration

@receiver(post_save, sender=Payslip)
def generate_payroll_journal(sender, instance, created, **kwargs):
    if instance.is_finalized and not instance.journal_created:
        PayrollAccountingIntegration.create_journal_from_payslip(instance, user=instance.created_by)
        instance.journal_created = True
        instance.save(update_fields=["journal_created"])