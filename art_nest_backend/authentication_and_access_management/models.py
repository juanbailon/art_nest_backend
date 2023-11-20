from django.db import models
from users.models import CustomUser
# Create your models here.

class PasswordResetOTP(models.Model):

    OTP = models.CharField(max_length=10, unique=True, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    expires_at = models.DateTimeField(null=False, blank=True)
    user_id =  models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)


class BlacklistedPasswordResetOTP(models.Model):

    OTP = models.OneToOneField(PasswordResetOTP, on_delete=models.CASCADE)
    blacklisted_at = models.DateTimeField(auto_now_add=True, null=False)


class FailedPasswordResetOTPAttempts(models.Model):

    OTP = models.OneToOneField(PasswordResetOTP, on_delete=models.CASCADE)
    failed_attempts = models.PositiveIntegerField(default=0, null=False, blank=False)
    last_failed_attempt = models.DateTimeField(auto_now=True, null=False)