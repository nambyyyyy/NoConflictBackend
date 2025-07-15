from rest_framework import permissions


class BaseIsOwnerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        raise NotImplementedError(
            "Implement has_object_permission in subclass"
        )


class IsOwnerOrRead(BaseIsOwnerPermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff


class IsOwnerOnly(BaseIsOwnerPermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff
