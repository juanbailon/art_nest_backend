from rest_framework import serializers
from .models import Follow


class FollowSerializer(serializers.ModelSerializer):    
    
    class Meta:
        model = Follow
        fields = '__all__'       
        extra_kwargs = {
            'id': {'read_only': True},
             }