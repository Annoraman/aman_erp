#accounts\models\module.py

from django.db import models
from core.models.base import BaseModel


class Module(BaseModel):

    name = models.CharField(max_length=100)

    code = models.CharField(
        max_length=50,
        unique=True
    )

    description = models.TextField(blank=True)

    class Meta:
        db_table = "accounts_module"

        ordering = ["name"]

        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name
        
