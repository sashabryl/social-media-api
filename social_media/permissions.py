from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated


class IsOwnerOrIsAuthenticatedReadAndCreateOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        is_owner = bool(request.user == obj.author)
        is_auth_or_read_only = bool(
            (
                request.user and
                request.user.is_authenticated and
                request.method in SAFE_METHODS + ["POST"]
            ) or request.method in SAFE_METHODS
        )
        return bool(is_owner or is_auth_or_read_only)