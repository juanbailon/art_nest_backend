from datetime import timedelta
from enum import Enum
from django.utils import timezone
from django.db.models import QuerySet
from users.models import CustomUser
from .models import TemporaryBlockUser
from .exeptions import TemporaryUserBlockError


class BlockReason(Enum):
    """
    Enumeration representing reasons for temporarily blocking a user.

    Attributes:
    - MAX_FAILED_OTP_ATTEMPTS_REACHED: Indicates that the user exceeded the maximum failed OTP attempts.
    """
    MAX_FAILED_OTP_ATTEMPTS_REACHED = "max_failed_otp_attempts_reached"


class TemporaryUserBlockManager:
    """
    Manager class for handling temporary user blocking.
    """

    @staticmethod
    def block_user(user: CustomUser, lifetime: timedelta, reason:str) -> TemporaryBlockUser:
        """
        Block a user for a specified period with a given reason.

        Args:
        - user (CustomUser): The user to be blocked.
        - lifetime (timedelta): The duration of the block.
        - reason (str): The reason for blocking the user.

        Returns:
        - TemporaryBlockUser: The created TemporaryBlockUser instance.
        """

        created_at = timezone.now()
        unblock_at = created_at + lifetime
        
        block_user_obj, created =  TemporaryBlockUser.objects.get_or_create(user= user,
                                                                            block_at= created_at,
                                                                            unblock_at = unblock_at,
                                                                            reason = reason
                                                                            )  
        
        return block_user_obj
    
        
    @staticmethod
    def check_user_block(user: CustomUser) -> None:
        """
        Check if a user is blocked; raises an error if blocked.

        Raises:
        - TemporaryUserBlockError: Raised if the user is blocked.
        """

        if TemporaryUserBlockManager.is_user_blocked(user= user):
            raise TemporaryUserBlockError(f"The user {user.username} is temporarily blocked")
        
        
    @staticmethod
    def is_user_blocked(user: CustomUser) -> bool:
        """
        Check if a user is currently blocked.
        """

        now = timezone.now()        
        user_block_query = TemporaryBlockUser.objects.filter(user=user, unblock_at__gt= now)

        return user_block_query.exists()
    
    @staticmethod
    def get_all_valid_temporary_user_blocks(user: CustomUser) -> QuerySet[TemporaryBlockUser]:
        """
        Retrieve all valid temporary user blocks for a user.

        Args:
        - user (CustomUser): The user for whom to retrieve blocks.

        Returns:
        - QuerySet[TemporaryBlockUser]: QuerySet of all valid temporary user blocks, ordered by unblock time.
        """
        
        now = timezone.now() 
        user_block_query = TemporaryBlockUser.objects.filter(user=user, unblock_at__gt= now).order_by("-unblock_at")

        return user_block_query

