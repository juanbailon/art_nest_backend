from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ForgotPasswordEmailSerializer
from .tasks import send_forgot_password_email_task

# Create your views here.

class SendForgotPasswordEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):        

        serializer = ForgotPasswordEmailSerializer(data= request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = request.data['email']
        send_forgot_password_email_task.delay(email, "hola a todas")

        return Response({'message': 'forgot password email has been send'}, status=status.HTTP_200_OK)
