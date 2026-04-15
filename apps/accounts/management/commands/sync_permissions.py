from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps

from apps.accounts.rbac.rbac_blueprint import RBAC_BLUEPRINT


class Command(BaseCommand):
    help = "Synchronize RBAC permissions from blueprint to database"

    def handle(self, *args, **options):

        Permission = apps.get_model("accounts", "Permission")

        created_count = 0

        with transaction.atomic():

            # Flatten all permissions from blueprint
            blueprint_permissions = set(
                perm
                for permissions in RBAC_BLUEPRINT.values()
                for perm in permissions
            )

            # Create missing permissions
            for code in blueprint_permissions:

                obj, created = Permission.objects.get_or_create(
                    code=code,
                    defaults={
                        "is_active": True
                    }
                )

                if created:
                    created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Permissions synced successfully. "
                    f"Newly created: {created_count}"
                )
            )