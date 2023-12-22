from rest_framework import serializers
from users.models import Avatar, ProfilePicture
from users.profile_image_handler import UserProfileImageManager
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
        

class UserFeedSerializer(serializers.ModelSerializer):

    username = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = UserPost
        fields = ['username',
                  'profile_image',
                  'post_image',
                 ]        


    def get_profile_image(self, obj: UserPost):

        profile_image_obj = UserProfileImageManager.get_user_profile_image(user= obj.user)
        
        if isinstance(profile_image_obj, ProfilePicture):
            return profile_image_obj.profile_picture.url
        elif isinstance(profile_image_obj, Avatar):
            return profile_image_obj.image.url
        else:
            return ""
        
    def get_username(self, obj: UserPost):

        return obj.user.username
