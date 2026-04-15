from functools import wraps
from django.http import HttpResponseForbidden

from apps.accounts.services.permission_service import PermissionService


def require_permission(permission_code):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not PermissionService.has_permission(
                request.user,
                permission_code
            ):
                return HttpResponseForbidden("Permission denied")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator