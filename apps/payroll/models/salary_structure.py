from django.db import models
from core.models.base import CompanyAwareModel

class SalaryStructure(CompanyAwareModel):
     
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("name", "company")
        indexes = [
            models.Index(fields=["company", "is_active"]),
        ]

    def __str__(self):
        return self.name