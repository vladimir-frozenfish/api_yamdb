from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.method in
                permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_superuser
                or request.user.role in ['admin', 'moderator'])


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)):
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if (request.method in permissions.SAFE_METHODS
             or (request.user.is_authenticated and request.user.is_admin)):
            return True
        return request.user.is_staff


class IsAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_admin

    
class IsSuperuser(permissions.BasePermission):
   
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated and request.user.is_superuser)
