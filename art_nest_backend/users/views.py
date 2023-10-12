from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import CustomUserSerializer
from .models import CustomUser

# Create your views here.

class CreateCustomUserView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]
