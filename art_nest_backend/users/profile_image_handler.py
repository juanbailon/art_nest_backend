from django.db.models.fields.files import ImageFieldFile
from .models import UserAvatar, Avatar, ProfilePicture, CustomUser


class UserAvatarManager:
    
    @staticmethod
    def set_user_avatar(user: CustomUser, avatar: Avatar) -> UserAvatar:
        ...
    
    @staticmethod
    def get_user_avatar(user: CustomUser) -> UserAvatar:
        ...
    
    @staticmethod
    def is_default_avatar(user: CustomUser) -> bool:
        ...

    @staticmethod
    def user_has_avatar(user: CustomUser) -> bool:
        ...


class ProfilePictureManager:
    
    @staticmethod
    def set_user_profile_picture(user: CustomUser, picture: ImageFieldFile) -> ProfilePicture:
        ...
    
    @staticmethod
    def get_user_profile_picture(user: CustomUser) -> ProfilePicture:
        ...
    
    @staticmethod
    def user_has_profile_picture(user: CustomUser) -> bool:
        ...



class UserProfileImageManager(UserAvatarManager, ProfilePictureManager):
    pass