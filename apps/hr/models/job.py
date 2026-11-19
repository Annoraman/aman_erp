# apps/hr/models/job.py

from django.db import models
from core.models.base import BaseModel


class Job(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # department = models.ForeignKey("Department", on_delete=models.CASCADE)
    company = models.ForeignKey("core.Company", on_delete=models.CASCADE)

    def __str__(self):
        return self.title