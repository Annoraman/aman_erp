from django.contrib import admin
from .models.employee import Employee
from .models.department import Department
from .models.job import Job
from .models.contract import Contract
from .models.job_grade import JobGrade
from .models.grade_step import GradeStep


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "company")
    search_fields = ("name",)
    list_filter = ("company",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "title",  "company",)
    search_fields = ("title",)
    list_filter = ("company",)

class ContractInline(admin.TabularInline): 
    model = Contract
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "department", "job", "company","created_by", "branch")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("department", "job", "company")
    inlines = [ContractInline]

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "basic_salary", "status", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("employee__first_name", "employee__last_name")

@admin.register(GradeStep)
class GradeStepAdmin(admin.ModelAdmin):
    pass

# @admin.register(JobGrade)
# class JobGradeAdmin(admin.ModelAdmin):
#     pass

admin.site.register(JobGrade)