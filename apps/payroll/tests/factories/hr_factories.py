#factories/hr_factories.py
import factory
from apps.hr.models.contract import  Contract
from apps.hr.models.grade_step import GradeStep
from apps.hr.models.job_grade import JobGrade
from apps.hr.models.employee import Employee
from apps.hr.models.job import Job
from apps.payroll.tests.factories.payroll_factories import SalaryStructureFactory
from apps.payroll.tests.factory import CompanyFactory, UserFactory


class JobFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = Job

    title = factory.Sequence(
        lambda n: f"Job-{n}"
    )
    company = factory.SubFactory(CompanyFactory)
    description = "Test Job" 
    
    
class JobGradeFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = JobGrade

    company = factory.SubFactory(CompanyFactory)

    grade = factory.Sequence(
        lambda n: f"Grade-{n}"
    )
    
    
class GradeStepFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = GradeStep

    grade = factory.SubFactory(JobGradeFactory)

    company = factory.SelfAttribute(
        "grade.company"
    )

    step = factory.Sequence(
        lambda n: f"Step-{n}"
    )
    
    

class EmployeeFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = Employee

    employee_code = factory.Sequence(
        lambda n: f"EMP{n:05d}"
    )

    first_name = "Test"

    last_name = factory.Sequence(
        lambda n: f"User{n}"
    )

    hire_date = factory.Faker("date")

    job_grade = factory.SubFactory(JobGradeFactory)

    grade_step = factory.SubFactory(
        GradeStepFactory,
        grade=factory.SelfAttribute("..job_grade")
    )

    company = factory.SelfAttribute(
        "job_grade.company"
    )

    job = factory.SubFactory(
        JobFactory
    )



class ContractFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = Contract

    employee = factory.SubFactory(EmployeeFactory)

    company = factory.SelfAttribute("employee.company")

    start_date = factory.Faker("date")

    basic_salary = 1000

    status = Contract.Status.ACTIVE

    salary_structure = factory.LazyAttribute(
        lambda o: SalaryStructureFactory(company=o.company)
    )

    job = factory.LazyAttribute(
        lambda o: JobFactory(company=o.company)
    )