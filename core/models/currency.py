# core/models/currency.py
from django.db import models
from .base import BaseModel


class Currency(BaseModel):
    code = models.CharField(max_length=3, unique=True)  # ISO
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, blank=True)

    decimal_places = models.PositiveSmallIntegerField(default=2)

    is_base = models.BooleanField(default=False)

    class Meta:
        db_table = "currencies"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return self.code