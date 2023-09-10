from rest_framework import permissions


class IsAdminOrReadOnly(permissions.IsAdminUser):
    """Права админу, остальным - только для чтения"""

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            or request.method in permissions.SAFE_METHODS
        )


class IsAdminAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Права админу или автору, остальным - только для чтения"""

    def has_object_permission(self, request, view, obj):
        if (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or request.user.is_superuser
        ):
            return True
        return False
