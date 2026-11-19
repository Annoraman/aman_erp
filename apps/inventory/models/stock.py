from django.db import models
from core.models.base import CompanyAwareModel


class Stock(CompanyAwareModel):

    product = models.ForeignKey("inventory.Product", on_delete=models.PROTECT)
    warehouse = models.ForeignKey("inventory.Warehouse", on_delete=models.PROTECT)

    quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "product", "warehouse"],
                name="uniq_stock_per_product_warehouse"
            )
        ]
        indexes = [
            models.Index(fields=["company", "product"]),
            models.Index(fields=["warehouse"]),
        ]