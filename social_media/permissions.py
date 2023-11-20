from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadCreateOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            (request.user.is_authenticated and request.method == "POST") or
            (
                request.method in ["DELETE", "PUT", "PATCH"] and
                obj.author.id == request.user.id
            )
        )