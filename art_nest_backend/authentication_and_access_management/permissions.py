from django.utils import timezone
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from users.models import CustomUser
from .temporary_user_block_handler import TemporaryUserBlockManager
from .serializers import UserEmailSerializer


class IsNotTemporarilyBlocked(permissions.BasePermission):
    """
    Custom permission to check if the user is not temporarily blocked.

    The view that implements this permission should have an email body parameter
    """

    def has_permission(self, request, view):

        user = request.user
        email = request.data.get('email', None)

        if user.is_authenticated:
            is_blocked = self.check_user_block(user= user)
            return not is_blocked
        
        serializer = UserEmailSerializer(data={'email': email})

        if serializer.is_valid(raise_exception= True):
            user_obj = CustomUser.objects.get(email= email)
            is_blocked = self.check_user_block(user= user_obj)
            return not is_blocked
        
    
    def check_user_block(self, user: CustomUser) -> bool:
        user_blocks = TemporaryUserBlockManager.get_all_valid_temporary_user_blocks(user= user)
        is_blocked = user_blocks.exists()

        if is_blocked:
            current_time = timezone.now()
            unblock_at = user_blocks[0].unblock_at
            time_delta = unblock_at - current_time
            minutes = time_delta.total_seconds() / 60

            raise PermissionDenied(detail=f"You are temporarily blocked, try again in {int(minutes)} minutes")
        
        return is_blocked
