#apps/accounts/api/admin/role_permission_admin_api.py

from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.services.role_permission_service import RolePermissionService


class AssignPermissionsToRoleAdminAPI(APIView):

    def post(self, request, role_id):

        permission_ids = request.data.get("permission_ids", [])

        RolePermissionService.assign_permissions(
            role_id=role_id,
            permission_ids=permission_ids
        )

        return Response({"status": "permissions_assigned"})