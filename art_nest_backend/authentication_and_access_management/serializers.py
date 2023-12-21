from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from users.models import CustomUser
from .models import PasswordResetOTP
from .otp_handler import PasswordResetOTPManager
from .exeptions import BlacklistedOTPError, MaxFailedAttemptsOTPError, ExpiredOTPError



class UserEmailSerializer(serializers.Serializer):

    email = serializers.EmailField()


    def validate(self, data):

        email = data['email']
        try:
            CustomUser.objects.get(email= email)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f'The emial {email} is NOT associated to any user')
        

        return data


class ValidatePasswordResetEmailOTPSerializer(serializers.Serializer):

    OTP = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def validate(self, data):
        
        email = data['email']
        try:
            user = CustomUser.objects.get(email= email)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'message': f'Invalid emial: {email}',
                                               'code': 'invalid_email'
                                               })
        
        otp = data['OTP']
        try:
            password_reset_otp_obj = PasswordResetOTP.objects.get(OTP= otp, user= user)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'message': f'Invalid OTP code',
                                               'code': 'invalid_otp'
                                               })
        
        try:
            PasswordResetOTPManager.check_max_failed_attempts(otp_instance= password_reset_otp_obj)
            PasswordResetOTPManager.check_blacklist(otp_instance= password_reset_otp_obj)
            PasswordResetOTPManager.check_expiration_date(otp_instance= password_reset_otp_obj)

        except BlacklistedOTPError:
            raise serializers.ValidationError({'message': f'Invalid OTP code, OTP is blacklisted',
                                               'code': 'blacklist_otp'
                                               })
        except MaxFailedAttemptsOTPError:
            raise serializers.ValidationError({'message': f'Invalid OTP code, max allowed attempts for OTP validation has been exceeded',
                                               'code': 'max_failed_attempts_exceeded'
                                               })
        except ExpiredOTPError:
            raise serializers.ValidationError({'message': f'Invalid OTP code, OTP is Expired',
                                               'code': 'expired_otp'
                                               })
        
        return data
        


class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=200, write_only=True)
    confirm_new_password = serializers.CharField(max_length=200, write_only=True)

    def validate(self, data):
        """
        Custom validation to ensure current_password matches the users DB password
        and new_password is confirmed correctly.
        """

        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')

        # Check if new_password and confirm_new_password match
        if new_password != confirm_new_password:
            raise serializers.ValidationError("New passwords do not match.")        

        user = self.context['request'].user
        try:
            validate_password(new_password, user)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({'new_password': e.messages})


        return data