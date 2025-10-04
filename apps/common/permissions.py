from rest_framework import permissions


class IsUnauthenticated(permissions.BasePermission):
    """
    Разрешает доступ только неавторизованным пользователям.
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated
    
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


class IsOwnerOrPartner(BaseIsOwnerPermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        if view.action == 'join' and obj.partner is None:
            return True

        if obj.partner is None:
            return obj.creator == request.user
            
        return obj.creator == request.user or obj.partner == request.user