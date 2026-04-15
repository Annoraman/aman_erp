#apps\accounts\models\user.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models.base import BaseModel
from core.models.company import Company
from core.models.branch import Branch
from .managers import UserManager
from apps.accounts.cache.permission_cache import PermissionCache


class User(AbstractUser, BaseModel):

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="users"
    )

    default_branch = models.ForeignKey(
        Branch,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="default_users"
    )

    # Optional personal info
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    job_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    email = models.EmailField(
        unique=True,
        db_index=True,
        db_collation="case_insensitive_email"
    )

    is_super_admin = models.BooleanField(
        default=False
        )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [ ]

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_permission(self, code, branch=None):
        permissions = PermissionCache.load_permissions(self, branch)
        return code in permissions

    # ✅ Compatibility with Django default permission system
    def has_perm(self, perm, obj=None):
        """
        Supports Django-style permissions:
        e.g. 'finance.add_journalentry'
        """

        # Superuser shortcut
        if self.is_superuser:
            return True

        # Extract permission code
        # 'finance.add_journalentry' → 'add_journalentry'
        code = perm.split(".")[-1]

        return self.has_permission(code)