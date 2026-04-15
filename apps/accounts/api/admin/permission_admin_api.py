#apps/accounts/api/admin/permission_admin_api.py

from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.selectors.permission_selector import PermissionSelector


class PermissionListAdminAPI(APIView):

    def get(self, request):

        permissions = PermissionSelector.list_permissions()

        data = [
            {
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "module": p.module
            }
            for p in permissions
        ]

        return Response(data)