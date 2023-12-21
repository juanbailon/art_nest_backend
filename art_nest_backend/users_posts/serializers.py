from rest_framework import serializers
from .models import UserPost


class UserPostSerializer(serializers.ModelSerializer):    
    
    class Meta:
        model = UserPost
        fields = ['id',
                  'user',
                  'post_image',
                  'created_at',
                 ]        
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
             }