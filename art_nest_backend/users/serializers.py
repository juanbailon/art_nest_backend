from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from users_posts.models import UserPost
from .models import CustomUser, Avatar, UserAvatar, ProfilePicture, UserProfile
from .profile_image_handler import UserProfileImageManager


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

        try:
            person = CustomUser.objects.create_user(password=password, **validated_data)
            UserProfileImageManager.set_user_avatar_to_default(user= person)
            
            presentation = "Hi! Welcome to the nest of this artist"
            UserProfile.objects.create(user= person, name= person.username, presentation= presentation)

        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})

        return person
    

class UpdateCustomUserSerializer(serializers.ModelSerializer):
    """ 
    This serializer is for updating the user info, but only NOT critical data
    that why the password field is not included 
    """
    
    class Meta:
        model = CustomUser
        fields = ['id',
                  'username',
                  'email',
                 ]        
        extra_kwargs = {
            'id': {'read_only': True},
             }


class PasswordUpdateSerializer(serializers.Serializer):

    current_password = serializers.CharField(max_length=200, write_only=True)
    new_password = serializers.CharField(max_length=200, write_only=True)
    confirm_new_password = serializers.CharField(max_length=200, write_only=True)

    def validate(self, data):
        """
        Custom validation to ensure current_password matches the users DB password
        and new_password is confirmed correctly.
        """

        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')

        # Check if new_password and confirm_new_password match
        if new_password != confirm_new_password:
            raise serializers.ValidationError("New passwords do not match.")

        
        # Check if current_password matches the user's actual password
        user = self.context['request'].user  # Assuming the user is already authenticated
        if not check_password(current_password, user.password):
            raise serializers.ValidationError("Current password is incorrect.")
        

        try:
            validate_password(new_password, user)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({'new_password': e.messages})


        return data
    

class SearchUsernameSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    presentation = serializers.CharField(source='userprofile.presentation', read_only=True)
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
                  'id',
                  'username',
                  'profile_image',
                  'presentation',
                  'is_following',
                 ]  
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {'read_only': True},        
             }
        
    
    def get_profile_image(self, obj: CustomUser):

        profile_image_obj = UserProfileImageManager.get_user_profile_image(user= obj)
        
        if isinstance(profile_image_obj, ProfilePicture):
            return profile_image_obj.profile_picture.url
        elif isinstance(profile_image_obj, Avatar):
            return profile_image_obj.image.url
        else:
            return ""
        
        
    def get_is_following(self, obj: CustomUser):
        request_user = self.context['request'].user
        return request_user.followed_users.filter(followed= obj.id).exists()




class AvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Avatar
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
             }
        

class UserAvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAvatar
        fields = ['id',
                  'avatar',
                  'user'
                  ]
        extra_kwargs = {
            'id': {'read_only': True},
             }
        

class ProfilePictureSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfilePicture
        fields = ['id',
                  'user',
                  'profile_picture',
                  ]
        extra_kwargs = {
            'id': {'read_only': True},            
             }
        

class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField()      


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    user_posts_images = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id',
                  'name',
                  'presentation',
                  'username',
                  'user_posts_images'
                  ]
        extra_kwargs = {
            'id': {'read_only': True},
            # 'username': {'read_only': True},        
             }
        
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_user_posts_images(self, obj):
        posts = UserPost.objects.filter(user= obj.user).order_by('-created_at')
        posts_images_urls = [p.post_image.url for p in posts]
        return posts_images_urls