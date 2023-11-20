from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from users.models import CustomUser
from .models import PasswordResetOTP, BlacklistedPasswordResetOTP, FailedPasswordResetOTPAttempts



class ForgotPasswordEmailSerializer(serializers.Serializer):

    email = serializers.EmailField()


    def validate(self, data):

        email = data['email']
        try:
            user = CustomUser.objects.get(email= email)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f'The emial {email} is NOT associated to any user')
        

        return data


