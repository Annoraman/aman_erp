from django.db import models
from core.models.base import CompanyAwareModel


class Warehouse(CompanyAwareModel):

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)

    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.PROTECT,
        related_name="warehouses"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="uniq_warehouse_company_code"
            )
        ]
        indexes = [
            models.Index(fields=["company", "code"]),
        ]

    def __str__(self):
        return f"{self.name}"