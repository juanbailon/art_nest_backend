from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import CustomUser
from .serializers import ForgotPasswordEmailSerializer
from .tasks import send_forgot_password_email_task
from .otp_handler import PasswordResetOTPManager

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
        password_reset_otp_obj = otp_manager.record_OTP(user= user)

        minutes = otp_manager.lifetime.total_seconds() / 60

        message = f"Your password reset OTP code is: {password_reset_otp_obj.OTP} \n Your code expires in {minutes} minutes"    

        send_forgot_password_email_task.delay(email, message)

        return Response({'message': 'forgot password email has been send'}, status=status.HTTP_200_OK)
    

