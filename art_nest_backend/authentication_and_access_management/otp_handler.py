import secrets
from datetime import timedelta
from enum import Enum
from django.conf import settings
from django.utils import timezone
from users.models import CustomUser
from .models import BlacklistedPasswordResetOTP, FailedPasswordResetOTPAttempts, PasswordResetOTP
from .exeptions import PasswordResetOTPError


class OTPCharacterSet(Enum):
    NUMBERS = "0123456789"
    LOWER_CASE_LETTERS = "".join(chr(i) for i in range(97, 123) )
    CAPITAL_CASE_LETTERS = "".join(chr(i) for i in range(65, 91) )
    ASCII_CHARS = "".join(chr(i) for i in range(33, 127) )


class OTPBlacklistManager:
    
    @staticmethod
    def check_blacklist(self, otp_code: str) -> None:
        """
        Checks if this OTP code is present in the OTP blacklist.  Raises
        `PasswordResetOTPError` if so.
        """

        if BlacklistedPasswordResetOTP.objects.filter(OTP__OTP=otp_code).exists():
            raise PasswordResetOTPError("This OTP code is blacklisted")
        

    @staticmethod
    def blacklist(self, OTP: PasswordResetOTP) -> BlacklistedPasswordResetOTP:
         
        blacklist_otp_obj, created = BlacklistedPasswordResetOTP.objects.get_or_create(OTP= OTP)
        return blacklist_otp_obj


class FailedOTPAttemptsManager:

    @staticmethod
    def record_failed_attempt(self, otp_instance: PasswordResetOTP) -> None:
        """
        Records a failed OTP attempt and raises an exception if the maximum
        allowed attempts are exceeded.
        """
        failed_attempts_obj, created = FailedPasswordResetOTPAttempts.objects.get_or_create(
            OTP=otp_instance
        )

        if failed_attempts_obj.failed_attempts >= settings.MAX_ALLOWED_ATTEMPS_FOR_OTP_VALIDATION:
            raise PasswordResetOTPError("Maximum number of failed OTP validation attempts exceeded")
        
        if not created:
            failed_attempts_obj.failed_attempts += 1
            failed_attempts_obj.save()

         
            
class PasswordResetOTPManager(OTPBlacklistManager, FailedOTPAttemptsManager):

    def __init__(self,
                 otp_length:int = settings.OTP_CODE_LENGTH,
                 charset:str = OTPCharacterSet.NUMBERS.value,
                 lifetime:timedelta = settings.PASSWORD_RESET_EMAIL_OTP_LIFETIME,
                 ) -> None:
        
        self.length = otp_length
        self.lifetime = lifetime
        self.charset = charset


    @staticmethod        
    def generate_OTP_code(otp_length:int = 6,
                 charset:str = OTPCharacterSet.NUMBERS.value
                ) -> str:
        
        return ''.join(secrets.choice(charset) for _ in range(otp_length))
    

    def record_OTP(self, user: CustomUser) -> PasswordResetOTP:
        
        otp = self.generate_OTP_code(otp_length= self.length, charset= self.charset)
        created_at = timezone.now()
        expires_at = created_at + self.lifetime

        password_reset_otp_obj = PasswordResetOTP.objects.create(OTP= otp,
                                        created_at= created_at,
                                        expires_at= expires_at,
                                        user = user
                                        )
        
        return password_reset_otp_obj


        