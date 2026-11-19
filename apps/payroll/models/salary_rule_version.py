# apps/payroll/models/salary_rule_version.py

from django.db import models
from core.models.base import CompanyAwareModel


class SalaryRuleVersion(CompanyAwareModel):

    rule = models.ForeignKey(
        "payroll.SalaryRule",
        related_name="versions",
        on_delete=models.CASCADE
    )

    version = models.IntegerField()

    sequence = models.IntegerField()

    condition = models.TextField(blank=True, null=True)
    formula = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("rule", "version")
        ordering = ["sequence"]
        
    def __str__(self):
        return self.rule.name  