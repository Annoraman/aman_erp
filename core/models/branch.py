from django.db import models
from .base import BaseModel
class Branch(BaseModel):
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE, related_name="branches")

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)

    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["company", "code"], name="uniq_branch_code_company")
        ]
        indexes = [
            models.Index(fields=["company", "code"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.company.code})"