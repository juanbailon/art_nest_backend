from django.db import models
from users.models import CustomUser
# Create your models here.

class PasswordResetOTP(models.Model):

    OTP = models.CharField(max_length=10, unique=True, blank=False, null=False)
    created_at = models.DateTimeField(null=False, blank=True)
    expires_at = models.DateTimeField(null=False, blank=True)
    user =  models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)


class BlacklistedPasswordResetOTP(models.Model):

    OTP = models.OneToOneField(PasswordResetOTP, on_delete=models.CASCADE)
    blacklisted_at = models.DateTimeField(auto_now_add=True, null=False)


class FailedPasswordResetOTPAttempts(models.Model):

    OTP = models.OneToOneField(PasswordResetOTP, on_delete=models.CASCADE)
    failed_attempts = models.PositiveIntegerField(default=0, null=False, blank=False)
    last_failed_attempt = models.DateTimeField(auto_now=True, null=False)


class TemporaryBlockUser(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    block_at = models.DateTimeField(auto_now_add=True)
    unblock_at = models.DateTimeField(blank=False, null=False)
    reason = models.TextField(blank=False, null=False)