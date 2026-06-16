from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


def role_required(*allowed_roles):
    def check_role(user):
        if user.is_superuser:
            return True
        if user.groups.filter(name__in=allowed_roles).exists():
            return True
        raise PermissionDenied
    return user_passes_test(check_role)
