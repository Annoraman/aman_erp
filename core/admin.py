
# core\admin.py
from django.contrib import admin
from .models.company import Company
from .models.branch import Branch


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "company", "created_at")
    search_fields = ("name",)
    list_filter = ("company",)
    ordering = ("id",)
