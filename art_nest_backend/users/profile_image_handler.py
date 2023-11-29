from django.db.models.fields.files import ImageFieldFile
from django.core.exceptions import ObjectDoesNotExist
from .models import UserAvatar, Avatar, ProfilePicture, CustomUser
from .exeptions import DefaultAvatarNotFoundError


class UserAvatarManager:
    
    @staticmethod
    def set_user_avatar(user: CustomUser, avatar: Avatar) -> UserAvatar:
         
        user_avatar_obj, created = UserAvatar.objects.update_or_create(user= user, avatar= avatar)
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
    

    @staticmethod
    def delete_user_avatar(user: CustomUser) -> None:
        user_avatar =  UserAvatarManager.get_user_avatar(user= user)

        if user_avatar is None:
            raise ValueError(f"User {user.username} does not have an avatar")

        user_avatar.delete()



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
    

    @staticmethod
    def delete_user_profile_picture(user: CustomUser) -> None:
        profile_pic_obj = ProfilePictureManager.get_user_profile_picture(user= user)

        if profile_pic_obj is None:
            raise ValueError(f"User {user.username} does not have an ProfilePicture")
        
        profile_pic_obj.delete()



class UserProfileImageManager(UserAvatarManager, ProfilePictureManager):
    
    @classmethod
    def set_user_profile_image(cls, user: CustomUser, image_data: Avatar | ImageFieldFile) -> UserAvatar | ProfilePicture:

        if type(image_data) == Avatar:
            return cls._set_user_avatar(user= user, avatar= image_data)
        
        if type(image_data) == ImageFieldFile:
            return cls._set_user_profile_picture(user= user, picture= image_data)
        
        raise ValueError(f"Unsupported image_data type {type(image_data)}. Expected Avatar or ImageFieldFile.")


    def _set_user_avatar(self, user: CustomUser, avatar: Avatar) -> UserAvatar:
        has_profile_pic = self.user_has_profile_picture(user= user)
        
        if has_profile_pic:
            self.delete_user_profile_picture(user= user)

        user_avatar_obj = self.set_user_avatar(user= user, avatar= avatar)

        return user_avatar_obj

    
    def _set_user_profile_picture(self, user: CustomUser, picture: ImageFieldFile) -> ProfilePicture:
        has_user_avatar =  self.user_has_avatar(user= user)

        if has_user_avatar:
            self.delete_user_avatar(user= user)

        profile_pic_obj = self.set_user_profile_picture(user= user, picture= picture)

        return profile_pic_obj
    