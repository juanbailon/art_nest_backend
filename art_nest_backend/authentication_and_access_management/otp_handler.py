import secrets
from datetime import datetime, timedelta
from enum import Enum
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from users.models import CustomUser
from .models import BlacklistedPasswordResetOTP, FailedPasswordResetOTPAttempts, PasswordResetOTP
from .exeptions import  BlacklistedOTPError, MaxFailedAttemptsOTPError, ExpiredOTPError


class OTPCharacterSet(Enum):
    NUMBERS = "0123456789"
    LOWER_CASE_LETTERS = "".join(chr(i) for i in range(97, 123) )
    CAPITAL_CASE_LETTERS = "".join(chr(i) for i in range(65, 91) )
    ASCII_CHARS = "".join(chr(i) for i in range(33, 127) )


class OTPBlacklistManager:
    
    @staticmethod
    def check_blacklist(otp_instance: PasswordResetOTP) -> None:
        """
        Checks if this OTP code is present in the OTP blacklist.  Raises
        `PasswordResetOTPError` if so.
        """

        if BlacklistedPasswordResetOTP.objects.filter(OTP=otp_instance).exists():
            raise BlacklistedOTPError(f"This OTP code {otp_instance.OTP} is blacklisted")
        

    @staticmethod
    def blacklist(OTP: PasswordResetOTP) -> BlacklistedPasswordResetOTP:
         
        blacklist_otp_obj, created = BlacklistedPasswordResetOTP.objects.get_or_create(OTP= OTP)
        return blacklist_otp_obj


class FailedOTPAttemptsManager:

    @staticmethod
    def record_failed_attempt(otp_instance: PasswordResetOTP) -> FailedPasswordResetOTPAttempts:
        """
        Records a failed OTP attempt and raises an exception if the maximum
        allowed attempts are exceeded.
        """
        max_allowed_failed_attempts = settings.MAX_ALLOWED_ATTEMPS_FOR_OTP_VALIDATION
        
        failed_attempts_obj, created = FailedPasswordResetOTPAttempts.objects.get_or_create(
            OTP=otp_instance
        )
        
        if failed_attempts_obj.failed_attempts >= max_allowed_failed_attempts:
            
            raise MaxFailedAttemptsOTPError("Maximum number of failed OTP validation attempts exceeded")
                
        failed_attempts_obj.failed_attempts += 1
        failed_attempts_obj.save()
        
        if created:
            return failed_attempts_obj
        
        if failed_attempts_obj.failed_attempts >= max_allowed_failed_attempts:
            
            OTPBlacklistManager.blacklist(otp_instance)
            raise MaxFailedAttemptsOTPError("Max validation attempts exceeded. OTP was balcklisted ")
        
        return failed_attempts_obj


    @staticmethod
    def check_max_failed_attempts(otp_instance: PasswordResetOTP) -> None:

        try:
            failed_attempts_obj= FailedPasswordResetOTPAttempts.objects.get(
                OTP=otp_instance
            )
        except ObjectDoesNotExist:
            """
            here we return None because if the instance DOES NOT exist this
            means that the user has never input his OTP code wrong for a validation
            """
            return None
        
        if failed_attempts_obj.failed_attempts >= settings.MAX_ALLOWED_ATTEMPS_FOR_OTP_VALIDATION:
            raise MaxFailedAttemptsOTPError("Maximum number of failed OTP validation attempts exceeded")
         
            
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
    

    def _generate_valid_OTP_code(self, user: CustomUser, max_iterations: int) -> str | None:

        for _ in range(max_iterations):
            otp_code = self.generate_OTP_code(otp_length= self.length, charset= self.charset)
            flag = self.is_valid_OTP_candidate(otp_code= otp_code, user= user)

            if flag:
                return otp_code

    
    def record_OTP(self, user: CustomUser) -> PasswordResetOTP:
        
        otp = self._generate_valid_OTP_code(user= user, max_iterations=5)

        created_at = timezone.now()
        expires_at = created_at + self.lifetime

        password_reset_otp_obj = PasswordResetOTP.objects.create(OTP= otp,
                                        created_at= created_at,
                                        expires_at= expires_at,
                                        user = user
                                        )
        
        return password_reset_otp_obj
    

    def is_valid_OTP_candidate(self,
                               otp_code: str,
                            #    created_at: datetime,
                            #    exprires_at: datetime,
                               user: CustomUser
                               ) -> bool:
        
        my_query = PasswordResetOTP.objects.filter(user= user, OTP= otp_code)

        return not my_query.exists()
    

    @staticmethod
    def is_OTP_expired(otp_instance: PasswordResetOTP) -> bool:
        current_time = timezone.now()
        expires_at = otp_instance.expires_at

        return current_time > expires_at
    

    @staticmethod
    def check_expiration_date(otp_instance: PasswordResetOTP) -> None:
        flag = PasswordResetOTPManager.is_OTP_expired(otp_instance)

        if flag:
            raise ExpiredOTPError("The OTP code is expired")
        
    
    @staticmethod
    def get_all_valid_user_OTPs(user: CustomUser) -> QuerySet[PasswordResetOTP]:

        current_time = timezone.now()
        
        not_expired_otps = PasswordResetOTP.objects.filter(expires_at__gt= current_time, user= user)
        not_expired_otps_ids = not_expired_otps.values_list('id', flat=True)
        
        blacklisted_otps = BlacklistedPasswordResetOTP.objects.filter(OTP__in= list(not_expired_otps_ids) )
        blacklisted_otps_ids = blacklisted_otps.values_list('id', flat=True)
        
        valid_otps = not_expired_otps.exclude(OTP__in= list(blacklisted_otps_ids)).order_by("-created_at")
        
        return valid_otps
    
    
    @staticmethod
    def get_all_user_OTPs(user: CustomUser) -> QuerySet[PasswordResetOTP]:

        return PasswordResetOTP.objects.filter(user= user)


        