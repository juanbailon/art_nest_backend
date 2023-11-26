from django.shortcuts import render
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework import generics, permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from users.models import CustomUser
from users.permissions import IsProfileOwnerPermission
from .serializers import ForgotPasswordEmailSerializer, ValidatePasswordResetEmailOTPSerializer, SetNewPasswordSerializer
from .tasks import send_forgot_password_email_task
from .otp_handler import PasswordResetOTPManager
from .exeptions import MaxFailedAttemptsOTPError
from .models import PasswordResetOTP

# Create your views here.

class SendForgotPasswordEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):        

        serializer = ForgotPasswordEmailSerializer(data= request.data)
        
        if not serializer.is_valid():              
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

        email = request.data['email']
        user = CustomUser.objects.get(email= email)

        otp_manager = PasswordResetOTPManager()
        PasswordResetOTPManager.blacklist_all_valid_user_otps(user= user)

        password_reset_otp_obj = otp_manager.record_OTP(user= user)

        minutes = otp_manager.lifetime.total_seconds() / 60

        message = f"Your password reset OTP code is: {password_reset_otp_obj.OTP} \n Your code expires in {minutes} minutes"    

        send_forgot_password_email_task.delay(email, message)

        return Response({'message': 'forgot password email has been send'}, status=status.HTTP_200_OK)
    


class ValidateForgotPasswordEmailOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    
    def post(self, request):        

        serializer = ValidatePasswordResetEmailOTPSerializer(data= request.data)

        try:
            serializer.is_valid(raise_exception=True)

        except serializers.ValidationError as e:
            error_code = e.detail['code'][0]

            if('invalid_otp' != error_code):
                raise e
            
            self.handle_invalid_otp(serializer= serializer)


        email = serializer.data.get('email')
        otp_code = serializer.data.get('OTP')
        user = CustomUser.objects.get(email= email)

        self.blacklist_the_valid_otp(user= user, otp_code= otp_code)
        access_token = self.generate_access_token(user= user)

        return Response({'message': 'OTP validation sucessfull',
                         'access': f'{access_token}'
                         },
                        status= status.HTTP_200_OK
                        )
    
    
    def handle_invalid_otp(self, serializer) -> None:

        email = serializer.data.get('email')

        # here we dont nedd to handle the ObjectDoesNotExist exection because
        # the serializer should had alredy check that a user whit this email exist
        user = CustomUser.objects.get(email= email)
        
        otp_objs = PasswordResetOTPManager.get_all_valid_user_OTPs(user= user)
        try:
            self.record_failed_validation_attempt(otp_instance= otp_objs[0])

        except MaxFailedAttemptsOTPError as e:
            raise serializers.ValidationError({'message': str(e),
                                               'code': 'invalid_otp'
                                               })
        except IndexError as e:
            raise serializers.ValidationError({'message': f'No valid OTPs found for this user',
                                               'code': 'invalid_otp'
                                               })


    def record_failed_validation_attempt(self, otp_instance: PasswordResetOTP) -> None:

        PasswordResetOTPManager.record_failed_attempt(otp_instance= otp_instance)

        remaining_attempts = PasswordResetOTPManager.get_remaining_attempts(otp_instance= otp_instance)

        raise MaxFailedAttemptsOTPError(f"Invalid OTP code, you have {remaining_attempts} attempts left")
                                            
    

    def blacklist_the_valid_otp(self, user: CustomUser, otp_code: str) -> None:
        # here we know that get_OTP wont retunr None since the validations of
        # the serializer have alredy been pass when this method is call
        OTP = PasswordResetOTPManager.get_OTP(user= user, otp_code= otp_code) 
        PasswordResetOTPManager.blacklist(OTP= OTP)

    
    def generate_access_token(self, user: CustomUser) -> str:
        access_token = AccessToken.for_user(user)

        try:
            lifetime = settings.SIMPLE_JWT['FORGOT_PASSWORD_ACCESS_TOKEN_LIFETIME']
        except KeyError:
            # Handle the case when the setting is not defined
            raise ImproperlyConfigured("FORGOT_PASSWORD_ACCESS_TOKEN_LIFETIME is not defined in SIMPLE_JWT settings.")

        access_token.set_exp(lifetime= lifetime)

        return access_token.__str__()

    

class SetNewUserPasswordView(APIView):
    """ this view updates the user password, this change can only be done through a PUT, NOT a PATCH """
    
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = SetNewPasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        new_password = serializer.validated_data['new_password']
        user = request.user
        print(user)
        user.set_password(new_password)
        user.save()

        return Response("New password set successfully", status=status.HTTP_200_OK)