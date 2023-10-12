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
        
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        person = CustomUser(**validated_data)
        person.set_password(password)
        person.save()
        
        return person