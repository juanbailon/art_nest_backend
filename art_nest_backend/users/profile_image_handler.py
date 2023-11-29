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
    def user_has_avater(user: CustomUser) -> bool:
        ...
        

class ProfilePictureManager:
    
    @staticmethod
    def set_user_profile_picture(user: CustomUser, avatar: Avatar) -> UserAvatar:
        ...
    
    @staticmethod
    def get_user_profile_picture(user: CustomUser) -> UserAvatar:
        ...
    
    @staticmethod
    def user_has_profile_picture(user: CustomUser) -> bool:
        ...



class UserProfileImageManager(UserAvatarManager, ProfilePictureManager):
    pass