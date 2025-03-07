from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only admins full access, others can only read.
    """

    def has_permission(self, request, view):
        # Allow read-only permissions (GET, HEAD, OPTIONS) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow write permissions only for admins
        return request.user and request.user.is_staff

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Owners can edit/delete, others can only read.
    """

    def has_object_permission(self, request, view, obj):
        # Allow read-only access (GET, HEAD, OPTIONS) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow write access only to the owner of the object
        return obj.user == request.user
