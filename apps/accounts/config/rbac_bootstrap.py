from django.db import transaction
from apps.accounts.models import Role, Permission, RolePermission
from apps.accounts.cache.permission_cache import PermissionCache
from ..rbac.rbac_blueprint import RBAC_BLUEPRINT


class RBACBootstrapService:

    @staticmethod
    @transaction.atomic
    def initialize_company(company, created_by=None):

        permission_objects = {}

        # -------------------------------------------------
        # 1️⃣ Create Permissions
        # -------------------------------------------------
        for module, permissions in RBAC_BLUEPRINT.items():

            for code in permissions:

                module_name, action = code.split(".")

                permission, _ = Permission.objects.get_or_create(
                    company=company,
                    code=code,
                    defaults={
                        "name": code.replace(".", " ").title(),
                        "module": module,
                        "action": action.upper(),
                        "is_system": True,
                        "created_by": created_by,
                    },
                )

                permission_objects[code] = permission

        # -------------------------------------------------
        # 2️⃣ Create System Roles
        # -------------------------------------------------
        super_admin, _ = Role.objects.get_or_create(
            company=company,
            code="SUPER_ADMIN",
            defaults={
                "name": "Super Administrator",
                "is_system": True,
                "created_by": created_by,
            },
        )

        admin, _ = Role.objects.get_or_create(
            company=company,
            code="ADMIN",
            defaults={
                "name": "Administrator",
                "is_system": True,
                "created_by": created_by,
            },
        )

        employee, _ = Role.objects.get_or_create(
            company=company,
            code="EMPLOYEE",
            defaults={
                "name": "Employee",
                "is_system": True,
                "created_by": created_by,
            },
        )

        # -------------------------------------------------
        # 3️⃣ Assign Permissions to Roles
        # -------------------------------------------------
        role_permissions = []

        for permission in permission_objects.values():

            # Super Admin → all permissions
            role_permissions.append(
                RolePermission(
                    role=super_admin,
                    permission=permission,
                    created_by=created_by,
                )
            )

            # Admin → everything
            role_permissions.append(
                RolePermission(
                    role=admin,
                    permission=permission,
                    created_by=created_by,
                )
            )

            # Employee → only VIEW
            if permission.action == "VIEW":
                role_permissions.append(
                    RolePermission(
                        role=employee,
                        permission=permission,
                        created_by=created_by,
                    )
                )

        RolePermission.objects.bulk_create(
            role_permissions,
            ignore_conflicts=True
        )

        return {
            "roles": [super_admin, admin, employee],
            "permissions_count": len(permission_objects),
        }
