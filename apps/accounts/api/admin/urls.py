#apps/accounts/api/admin/urls.py

from django.urls import path

from .role_admin_api import *
from .permission_admin_api import *
from .role_permission_admin_api import *
from .user_role_admin_api import *

urlpatterns = [

    path("roles/", RoleListCreateAdminAPI.as_view()),
    path("roles/<int:role_id>/", RoleUpdateDeleteAdminAPI.as_view()),

    path("permissions/", PermissionListAdminAPI.as_view()),

    path(
        "roles/<int:role_id>/permissions/",
        AssignPermissionsToRoleAdminAPI.as_view()
    ),

    path(
        "users/<int:user_id>/roles/",
        AssignRoleToUserAdminAPI.as_view()
    ),
]