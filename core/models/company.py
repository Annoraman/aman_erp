from django.db import models
from .base import BaseModel


class Company(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return self.name


