from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):    
    
    class Meta:
        model = CustomUser
        fields = ['id',
                  'username',
                  'email',
                  'password', 
                 ]        
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
             }