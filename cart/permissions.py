from rest_framework.permissions import BasePermission

class IsAuthorPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.is_authenticated and str(obj.user).lower() == str(request.user.email).lower())

class IsCustomerPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user.profile_customer:
                return bool(request.user.is_authenticated)
        except:
            return False