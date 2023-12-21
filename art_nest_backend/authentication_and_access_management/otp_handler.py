import secrets
from datetime import timedelta
from enum import Enum
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from users.models import CustomUser
from .models import BlacklistedPasswordResetOTP, FailedPasswordResetOTPAttempts, PasswordResetOTP
from .exeptions import  BlacklistedOTPError, MaxFailedAttemptsOTPError, ExpiredOTPError


class OTPCharacterSet(Enum):
    """
    Enumeration representing the different character sets for OTP generation.

    Attributes:
    - NUMBERS: Numeric characters (0-9).
    - LOWER_CASE_LETTERS: Lowercase alphabetical characters (a-z).
    - CAPITAL_CASE_LETTERS: Uppercase alphabetical characters (A-Z).
    - ASCII_CHARS: All ASCII characters from '!' to '~'.
    """

    NUMBERS = "0123456789"
    LOWER_CASE_LETTERS = "".join(chr(i) for i in range(97, 123) )
    CAPITAL_CASE_LETTERS = "".join(chr(i) for i in range(65, 91) )
    ASCII_CHARS = "".join(chr(i) for i in range(33, 127) )


class OTPBlacklistManager:
    """
    Manages the blacklisting of password reset OTP codes.
    """
    
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
        """
        Blacklists the given OTP code.
        
        Returns:
        - BlacklistedPasswordResetOTP: The blacklisted OTP instance.
        """
         
        blacklist_otp_obj, created = BlacklistedPasswordResetOTP.objects.get_or_create(OTP= OTP)
        return blacklist_otp_obj
    
    
    @staticmethod
    def blacklist_all_valid_user_otps(user: CustomUser) -> QuerySet[PasswordResetOTP]:
        """ 
           Blacklists all valid OTPs associated with a given user.

            Returns:
            - QuerySet[PasswordResetOTP]: A queryset containing all the OTPs that were blacklisted
        """
        all_valid_user_otps = PasswordResetOTPManager.get_all_valid_user_OTPs(user= user)

        if all_valid_user_otps.exists():
            for otp in all_valid_user_otps:
                PasswordResetOTPManager.blacklist(OTP= otp)

        return all_valid_user_otps


class FailedOTPAttemptsManager:
    """
    Manages failed OTP validation attempts.
    """

    @staticmethod
    def record_failed_attempt(otp_instance: PasswordResetOTP) -> FailedPasswordResetOTPAttempts:
        """
        Records a failed OTP attempt and raises an exception if the maximum
        allowed attempts are exceeded.

        Raises:
        - MaxFailedAttemptsOTPError: If the maximum allowed attempts are exceeded.
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
            raise MaxFailedAttemptsOTPError("Max validation attempts exceeded. OTP was blacklisted ")
        
        return failed_attempts_obj


    @staticmethod
    def check_max_failed_attempts(otp_instance: PasswordResetOTP) -> None:
        """
        Checks if the maximum allowed failed OTP attempts are exceeded.

        Parameters:
        - otp_instance (PasswordResetOTP): The OTP instance for which the attempts are checked.

        Raises:
        - MaxFailedAttemptsOTPError: If the maximum failed OTP attempts are exceeded.
        """
        
        failed_attempts_obj = FailedOTPAttemptsManager.get_failed_otp_attempt(otp_instance= otp_instance)

        if failed_attempts_obj is None:
            return None
        
        if failed_attempts_obj.failed_attempts >= settings.MAX_ALLOWED_ATTEMPS_FOR_OTP_VALIDATION:
            raise MaxFailedAttemptsOTPError("Maximum number of failed OTP validation attempts exceeded")


    @staticmethod
    def get_failed_attempts_count(otp_instance: PasswordResetOTP) -> int:
        """
        Gets the count of failed OTP validation attempts.

        Parameters:
        - otp_instance (PasswordResetOTP): The OTP instance for which the attempts count is retrieved.
        """

        failed_attempts_obj = FailedOTPAttemptsManager.get_failed_otp_attempt(otp_instance= otp_instance)

        if failed_attempts_obj is None:
            return 0
        
        return failed_attempts_obj.failed_attempts        


    @staticmethod
    def get_remaining_attempts(otp_instance: PasswordResetOTP) -> int:
        """
        Calculate the remaining attempts for the user to validate their OTP.

        Parameters:
        - otp_instance (PasswordResetOTP): The OTP instance for which the remaining attempts are calculated.
        """
        num_failed_attempts = FailedOTPAttemptsManager.get_failed_attempts_count(otp_instance= otp_instance)
        
        count = settings.MAX_ALLOWED_ATTEMPS_FOR_OTP_VALIDATION - num_failed_attempts

        return count


    @staticmethod
    def get_failed_otp_attempt(otp_instance: PasswordResetOTP) -> FailedPasswordResetOTPAttempts | None:
        """
        Gets the failed OTP attempts instance for a given OTP.

        Parameters:
        - otp_instance (PasswordResetOTP): The OTP instance for which the failed attempts instance is retrieved.

        Returns:
        - FailedPasswordResetOTPAttempts | None: The failed OTP attempts instance or None if not found.
        """

        try:
            failed_attempts_obj= FailedPasswordResetOTPAttempts.objects.get(
                OTP= otp_instance
            )
        except ObjectDoesNotExist:
            """
            here we return None because if the instance DOES NOT exist this
            means that the user has never input his OTP code wrong for a validation
            """
            return None
        
        return failed_attempts_obj
         
            
class PasswordResetOTPManager(OTPBlacklistManager, FailedOTPAttemptsManager):
    """
    Manages the generation, validation, and expiration of OTP codes.
    """

    def __init__(self,
                 otp_length:int = settings.OTP_CODE_LENGTH,
                 charset:str = OTPCharacterSet.NUMBERS.value,
                 lifetime:timedelta = settings.PASSWORD_RESET_EMAIL_OTP_LIFETIME,
                 ) -> None:
        """
        Initializes the OTP manager with custom parameters.

        Parameters:
        - otp_length (int): The length of the OTP code.
        - charset (str): The character set used for generating OTP codes.
        - lifetime (timedelta): The lifetime of generated OTP codes.
        """
        
        self.length = otp_length
        self.lifetime = lifetime
        self.charset = charset


    @staticmethod        
    def generate_OTP_code(otp_length:int = 6,
                 charset:str = OTPCharacterSet.NUMBERS.value
                ) -> str:
        """
        Generates a random OTP code.

        Parameters:
        - otp_length (int): The length of the OTP code.
        - charset (str): The character set used for generating OTP codes.
        """
        
        return ''.join(secrets.choice(charset) for _ in range(otp_length))
    

    def _generate_valid_OTP_code(self, user: CustomUser, max_iterations: int) -> str | None:
        """
        Generates a valid OTP code for a user.

        Parameters:
        - user (CustomUser): The user for whom the OTP code is generated.
        - max_iterations (int): The maximum number of iterations to attempt.

        Returns:
        - str | None: The generated valid OTP code or None if no valid code is generated.

        Is very unlikely that the reuturn value will be None. The bigger the otp code length
        the less likely it will be that the returned value will be none
        """

        for _ in range(max_iterations):
            otp_code = self.generate_OTP_code(otp_length= self.length, charset= self.charset)
            flag = self.is_valid_OTP_candidate(otp_code= otp_code, user= user)

            if flag:
                return otp_code

    
    def record_OTP(self, user: CustomUser) -> PasswordResetOTP:
        """
        Records an OTP for a user.

        Parameters:
        - user (CustomUser): The user for whom the OTP is recorded.

        Returns:
        - PasswordResetOTP: The recorded OTP instance.
        """
        
        otp = self._generate_valid_OTP_code(user= user, max_iterations=5)

        created_at = timezone.now()
        expires_at = created_at + self.lifetime

        password_reset_otp_obj = PasswordResetOTP.objects.create(OTP= otp,
                                        created_at= created_at,
                                        expires_at= expires_at,
                                        user = user
                                        )
        
        return password_reset_otp_obj
    

    def is_valid_OTP_candidate(self, otp_code: str, user: CustomUser) -> bool:
        """
        Checks if an OTP code is a valid candidate for a user.
        """     
        my_query = PasswordResetOTP.objects.filter(user= user, OTP= otp_code)

        return not my_query.exists()
    

    @staticmethod
    def is_OTP_expired(otp_instance: PasswordResetOTP) -> bool:
        """
        Checks if an OTP has expired.

        Parameters:
        - otp_instance (PasswordResetOTP): The OTP instance to check.
        """
        current_time = timezone.now()
        expires_at = otp_instance.expires_at

        return current_time > expires_at
    

    @staticmethod
    def check_expiration_date(otp_instance: PasswordResetOTP) -> None:
        """
        Checks the expiration date of an OTP and raises an exception if it is expired.

        Raises:
        - ExpiredOTPError: If the OTP is expired.
        """
        flag = PasswordResetOTPManager.is_OTP_expired(otp_instance)

        if flag:
            raise ExpiredOTPError("The OTP code is expired")
        
    
    @staticmethod
    def get_all_valid_user_OTPs(user: CustomUser) -> QuerySet[PasswordResetOTP]:
        """
        Gets all valid OTPs for a user.

        Returns:
        - QuerySet[PasswordResetOTP]: A queryset containing all valid OTPs.
        """
        current_time = timezone.now()
        
        not_expired_otps = PasswordResetOTP.objects.filter(expires_at__gt= current_time, user= user)
        not_expired_otps_ids = not_expired_otps.values_list('id', flat=True)
        
        blacklisted_otps = BlacklistedPasswordResetOTP.objects.filter(OTP__in= list(not_expired_otps_ids) )
        blacklisted_otps_ids = blacklisted_otps.values_list('id', flat=True)
        
        valid_otps = not_expired_otps.exclude(OTP__in= list(blacklisted_otps_ids)).order_by("-created_at")
        
        return valid_otps
    
    
    @staticmethod
    def get_all_user_OTPs(user: CustomUser) -> QuerySet[PasswordResetOTP]:
        """
        Gets all OTPs for a user.

        Returns:
        - QuerySet[PasswordResetOTP]: A queryset containing all OTPs.
        """

        return PasswordResetOTP.objects.filter(user= user)
    

    @staticmethod
    def get_OTP(user: CustomUser, otp_code: str) -> PasswordResetOTP | None:
        """
        Gets an OTP instance for a given user and OTP code.

        Parameters:
        - user (CustomUser): The user associated with the OTP.
        - otp_code (str): The OTP code.
        """

        try:
            return PasswordResetOTP.objects.get(user=user, OTP=otp_code)
        
        except ObjectDoesNotExist:
            return None


        