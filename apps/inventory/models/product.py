from django.db import models
from core.models.base import CompanyAwareModel


class Product(CompanyAwareModel):

    class ProductType(models.TextChoices):
        STOCK = "STOCK", "Stockable"
        SERVICE = "SERVICE", "Service"
        CONSUMABLE = "CONSUMABLE", "Consumable"

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)

    category = models.ForeignKey(
        "inventory.ProductCategory",
        on_delete=models.PROTECT,
        related_name="products"
    )

    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices
    )

    uom = models.ForeignKey(
        "core.UOM",
        on_delete=models.PROTECT
    )

    cost_price = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="uniq_product_company_code"
            )
        ]
        indexes = [
            models.Index(fields=["company", "code"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.name