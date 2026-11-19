from django.db import models

from core.models.company import Company


class ApprovalRule(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50)

    role = models.CharField(max_length=50)

    sequence = models.IntegerField()

    min_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    max_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    only_high_risk_supplier = models.BooleanField(default=False)

    department = models.ForeignKey("hr.Department", null=True, blank=True, on_delete=models.SET_NULL)

    is_active = models.BooleanField(default=True)

    priority = models.IntegerField(default=1)


