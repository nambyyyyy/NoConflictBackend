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


class IsOwnerOrPartner(BaseIsOwnerPermission):
    def has_object_permission(self, request, view, obj):
        # Если действие - 'join', и партнер еще не назначен,
        # то любой аутентифицированный пользователь может попытаться присоединиться.
        # Сам метод join() внутри проверит, не является ли он создателем.
        if request.user.is_staff:
            return True
        
        if view.action == 'join' and obj.partner is None:
            return True

        # Во всех остальных случаях - доступ только для участников
        if obj.partner is None:
            return obj.creator == request.user
            
        return obj.creator == request.user or obj.partner == request.user