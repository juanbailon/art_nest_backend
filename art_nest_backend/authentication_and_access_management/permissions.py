from rest_framework import permissions
from .temporary_user_block_handler import TemporaryUserBlockManager


class IsNotTemporarilyBlocked(permissions.BasePermission):
    """
    Custom permission to check if the user is not temporarily blocked.
    """
    def has_permission(self, request, view):
        user = request.user
        return  not TemporaryUserBlockManager.is_user_blocked(user)