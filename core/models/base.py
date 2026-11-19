from django.conf import settings
from django.db import models
from .managers import  CompanyManager


# -------------------------
# TIME + SOFT DELETE
# -------------------------
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    # soft delete behavior
    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save()


class AuditModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="%(class)s_created"
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated"
    )

    class Meta:
        abstract = True


# -------------------------
# BASE MODEL
# -------------------------
class BaseModel(TimeStampedModel, SoftDeleteModel, AuditModel):
    class Meta:
        abstract = True


# -------------------------
# MULTI COMPANY MODEL
# -------------------------
class CompanyAwareModel(BaseModel):
    company = models.ForeignKey("core.Company", on_delete=models.PROTECT)

    objects = CompanyManager()

    class Meta:
        abstract = True