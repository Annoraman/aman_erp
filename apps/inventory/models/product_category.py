from django.db import models
from core.models.base import CompanyAwareModel


class ProductCategory(CompanyAwareModel):

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="uniq_category_company_code"
            )
        ]
        indexes = [
            models.Index(fields=["company", "code"]),
        ]

    def __str__(self):
        return self.name