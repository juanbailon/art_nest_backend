from datetime import timedelta
from enum import Enum
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from users.models import CustomUser
from .models import TemporaryBlockUser
from .exeptions import TemporaryUserBlockError


class BlockReason(Enum):
    MAX_FAILED_OTP_ATTEMPTS_REACHED = "max_failed_otp_attempts_reached"


class TemporaryUserBlockManager:

    @staticmethod
    def block_user(user: CustomUser, lifetime: timedelta, reason:str) -> TemporaryBlockUser:

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

        if TemporaryUserBlockManager.is_user_blocked(user= user):
            raise TemporaryUserBlockError(f"The user {user.username} is temporarily blocked")
        
        
    @staticmethod
    def is_user_blocked(user: CustomUser) -> bool:

        now = timezone.now()        
        user_block_query = TemporaryBlockUser.objects.filter(user=user, unblock_at__gt= now)

        return user_block_query.exists()
       

