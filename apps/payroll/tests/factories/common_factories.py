import factory

from core.models.company import Company


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: f"Company {n}")
    code = factory.Sequence(lambda n: f"CMP{n:04d}")