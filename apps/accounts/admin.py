from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("ERP Information", {
            "fields": ("phone_number", "job_title"),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {
            "fields": ("phone_number", "job_title"),
        }),
    )
