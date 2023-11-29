from django.db.models.fields.files import ImageFieldFile
from django.core.exceptions import ObjectDoesNotExist
from .models import UserAvatar, Avatar, ProfilePicture, CustomUser
from .exeptions import DefaultAvatarNotFoundError


class UserAvatarManager:
    
    @staticmethod
    def set_user_avatar(user: CustomUser, avatar: Avatar) -> UserAvatar:
         
        user_avatar_obj, created = UserAvatar.objects.get_or_create(user= user, avatar= avatar)
        return user_avatar_obj
    
    @staticmethod
    def get_user_avatar(user: CustomUser) -> UserAvatar | None:
        try:
            user_avatar_obj = UserAvatar.objects.get(user= user)
        except ObjectDoesNotExist:
            return None
        
        return user_avatar_obj
    
    @staticmethod
    def has_default_avatar(user: CustomUser) -> bool:
        try:
            avatar =  Avatar.objects.get(avatar_name= 'default')
            UserAvatar.objects.get(user= user, avatar= avatar)

        except Avatar.DoesNotExist:
            raise DefaultAvatarNotFoundError("There is not Avatar object set as the dafault avatar")
        except UserAvatar.DoesNotExist:
            return False
        
        return True
        

    @staticmethod
    def user_has_avatar(user: CustomUser) -> bool:
        try:
            UserAvatar.objects.get(user= user)
        except ObjectDoesNotExist:
            return False
        
        return True



class ProfilePictureManager:
    
    @staticmethod
    def set_user_profile_picture(user: CustomUser, picture: ImageFieldFile) -> ProfilePicture:

        profile_picture_obj, created =  ProfilePicture.objects.update_or_create(user= user, profile_picture= picture)
        return profile_picture_obj
    
    @staticmethod
    def get_user_profile_picture(user: CustomUser) -> ProfilePicture | None:
        try:
            profile_picture_obj = ProfilePicture.objects.get(user= user)
        except ObjectDoesNotExist:
            return None

        return profile_picture_obj
    

    @staticmethod
    def user_has_profile_picture(user: CustomUser) -> bool:
        try:
            ProfilePicture.objects.get(user= user)
        except ObjectDoesNotExist:
            return False
        
        return True



class UserProfileImageManager(UserAvatarManager, ProfilePictureManager):
    pass