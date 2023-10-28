from rest_framework import permissions


class IsProfileOwnerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow requests for retrieving user's own information
        return  request.user.id == view.kwargs['pk']
    

    