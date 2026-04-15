#apps/accounts/api/admin/user_role_admin_api.py

from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.services.user_role_service import UserRoleService


class AssignRoleToUserAdminAPI(APIView):

    def post(self, request, user_id):

        role_ids = request.data.get("role_ids", [])

        UserRoleService.assign_roles(
            user_id=user_id,
            role_ids=role_ids
        )

        return Response({"status": "roles_assigned"})