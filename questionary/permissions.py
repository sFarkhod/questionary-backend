from rest_framework.permissions import BasePermission

# allow only admins to access the requested view
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
