#apps/accounts/api/admin/role_admin_api.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.models import Role
from apps.accounts.selectors.role_selector import RoleSelector
from apps.accounts.services.role_service import RoleService


class RoleListCreateAdminAPI(APIView):

    def get(self, request):

        roles = RoleSelector.list_roles()

        data = [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
            }
            for r in roles
        ]

        return Response(data)

    def post(self, request):

        role = RoleService.create_role(
            name=request.data["name"],
            description=request.data.get("description"),
            created_by=request.user
        )

        return Response(
            {"id": role.id},
            status=status.HTTP_201_CREATED
        )


class RoleUpdateDeleteAdminAPI(APIView):

    def put(self, request, role_id):

        RoleService.update_role(
            role_id=role_id,
            name=request.data.get("name"),
            description=request.data.get("description")
        )

        return Response({"status": "updated"})


    def delete(self, request, role_id):

        RoleService.delete_role(role_id)

        return Response({"status": "deleted"})
