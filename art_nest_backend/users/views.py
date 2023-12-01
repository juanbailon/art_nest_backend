from django.shortcuts import render
from rest_framework import generics, permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from .serializers import (  
    CustomUserSerializer, 
    UpdateCustomUserSerializer,
    PasswordUpdateSerializer, 
    SearchUsernameSerializer,
    AvatarSerializer,
    UserAvatarSerializer,
    ProfilePictureSerializer,
    ImageSerializer
    )
from .models import CustomUser, Avatar, ProfilePicture
from .permissions import IsProfileOwnerPermission
from .filters import UsernameFilter
from .exeptions import DefaultAvatarNotFoundError
from .profile_image_handler import UserProfileImageManager, AvatarManager


# Create your views here.


class CreateCustomUserView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]


class RetriveUpdateAndDeleteCustomUserView(generics.RetrieveUpdateDestroyAPIView):
    """ 
    This view lets the users consult and update his own data, in the updates the user 
    can NOT change the password, since this is consider a critical task and therefor is
    assing to an especific endpoint.

    Also lets the user delete it self from the database
    """
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsProfileOwnerPermission]
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomUserSerializer
        elif self.request.method in ('PUT', 'PATCH'):
            return UpdateCustomUserSerializer
        else:
            return CustomUserSerializer


class UpdateUserPasswordView(generics.UpdateAPIView):
    """ this view updates the user password, this change can only be done through a PUT, NOT a PATCH """
    
    serializer_class =  PasswordUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileOwnerPermission]
    queryset = CustomUser.objects.all()
    lookup_field = 'username'

    http_method_names = ['put'] # thsi makes only the PUT available and the PATCH inavailabe

    def put(self, request, *args, **kwargs):

        serializer = self.get_serializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        
        new_password = serializer.validated_data['new_password']
        user = request.user
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
    

class SearchUserByUsernameView(generics.ListAPIView):
    """
    API view for searching users by username.

    Requires authentication.

    Query Parameters:
    - `username` (string): Search for users whose username contains the specified string.

    Returns a list of users matching the search criteria.

    Example usage:
    - Search users by username: GET /search-username/?username=johndoe
    """

    queryset = CustomUser.objects.all()
    serializer_class = SearchUsernameSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = UsernameFilter


class ListAllAvatarsView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AvatarSerializer
    queryset = Avatar.objects.all()


class UserAvartarView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsProfileOwnerPermission]
    
    def post(self, request, username):
        user = request.user
        avatar_id = request.data.get('avatar')

        serializer = UserAvatarSerializer(data= {'user': user.id,
                                                 'avatar': avatar_id
                                                }
                                                )
        
        serializer.is_valid(raise_exception= True)

        avatar = AvatarManager.get_avatar_by_id(id= avatar_id)

        try:
            UserProfileImageManager.set_user_profile_image(user= user, image_data= avatar)
        except ValueError as e:
            raise serializers.ValidationError({'message': 'could not find any Avatar with the given values'})
        
        return Response({'message': 'Avatar set successfully as the user profile image'}, status= status.HTTP_200_OK)


    def put(self, request, username):
        user = request.user
        avatar_id = request.data.get('avatar')

        avatar = UserProfileImageManager.get_user_avatar(user= user)

        if avatar is None:
            raise serializers.ValidationError({'message': 'The user does not have an avatar'})

        serializer = UserAvatarSerializer(instance= avatar, data= {'avatar': avatar_id}, partial=True)
        serializer.is_valid(raise_exception= True)
        serializer.save()

        return Response({'message': 'user avatar updated successfully'}, status=status.HTTP_200_OK)
    


class ProfilePictureView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsProfileOwnerPermission]

    def post(self, request, username):
        user = request.user
        profile_pic_image = request.data.get('picture')

        serializer = ProfilePictureSerializer(data= {'user': user.id,
                                                    'profile_picture': profile_pic_image
                                                    }
                                                    )
        
        serializer.is_valid(raise_exception= True)

        try:
            UserProfileImageManager.set_user_profile_image(user= user, image_data= profile_pic_image)
        except ValueError as e:
            raise serializers.ValidationError({'message': 'The picture provided is the wrong format'})
        
        return Response({'message': 'Profile picture created successfully'}, status= status.HTTP_201_CREATED)


    def put(self, request, username):
        user = request.user
        profile_pic_image = request.data.get('picture')

        profile_picture_obj = UserProfileImageManager.get_user_profile_picture(user= user)

        if profile_picture_obj is None:
            raise serializers.ValidationError({'message': 'The user does not have a profile picture'})

        serializer = ProfilePictureSerializer(instance= profile_picture_obj,
                                              data= {'profile_picture': profile_pic_image},
                                              partial= True
                                            )
        
        serializer.is_valid(raise_exception= True)
        UserProfileImageManager.set_user_profile_image(user= user, image_data= profile_pic_image)   
             
        return Response({'message': 'user profile picture updated successfully'}, status=status.HTTP_200_OK)
    

    def get(self, request, username):
        user = request.user

        profile_img_object = UserProfileImageManager.get_user_profile_image(user= user)


        if isinstance(profile_img_object, Avatar):
            img_field = profile_img_object.image

        elif isinstance(profile_img_object, ProfilePicture):
            img_field = profile_img_object.profile_picture

        else:
            return Response({'message': 'The user does not have any Avatar of picture set as his profile image'})
        

        serializer = ImageSerializer(data= {'image': img_field},)
        serializer.is_valid(raise_exception= True)
        full_image_url = request.build_absolute_uri(img_field.url)
        
        return Response({'image': full_image_url}, status= status.HTTP_200_OK)
    

    def delete(self, request, username):
        user = request.user

        try:
            has_no_profile_img = UserProfileImageManager.has_default_avatar(user= user)
        except DefaultAvatarNotFoundError:
            return Response({'message': 'Please contact our client support'}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)

        if has_no_profile_img:
            return Response({"message": "You dont have any profile image to be deleted"}, status= status.HTTP_200_OK)

        UserProfileImageManager.delete_user_profile_image(user= user)
        UserProfileImageManager.set_user_avatar_to_default(user= user)

        return Response({"message": "Profile image deleted successfully"}, status= status.HTTP_200_OK)
    

class GetCustomUserID(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        id = user.id

        return Response({'user_id': id}, status= status.HTTP_200_OK)
    

class GetCustomUserUsername(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        username = request.user.username        

        return Response({'username': username}, status= status.HTTP_200_OK)


