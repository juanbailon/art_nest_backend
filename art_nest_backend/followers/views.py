from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.utils import IntegrityError
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import CustomUser
from .serializers import FollowSerializer
from .models import Follow

# Create your views here.


# class FollowNewUserView2(generics.CreateAPIView):
#     serializer_class = FollowSerializer
#     permission_classes = [permissions.IsAuthenticated]
    


class FollowNewUserView(APIView):
    """
    API view to follow a new user.

    Requires authentication. Users can follow other users by providing either
    the user ID or the username in the URL.

    Example usage:
    - Follow user by ID: POST /follow/123
    - Follow user by username: POST /follow/johndoe
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            if(type(pk)==int):
                followed_user = CustomUser.objects.get(id=pk)
            else:
                followed_user = CustomUser.objects.get(username=pk)
        
        except ObjectDoesNotExist: 
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except ValueError:
            return Response({'error': 'Value Error'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        if(request.user.id == followed_user.id):
            return Response({'error': 'You CAN NOT follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            follow = Follow.objects.create(follower= request.user, followed=followed_user)

        except IntegrityError as e:

            if 'unique constraint' in str(e).lower():
                return Response({'error': f'You are already following this user: {followed_user.username}'}, status=status.HTTP_409_CONFLICT)
            else:
                return Response({'message': 'An IntegrityError occurred. Please check your request.'}, status=status.HTTP_409_CONFLICT)

        except PermissionDenied:
            return Response({'error': 'You do not have permission to follow this user'}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        return Response({'message': f'success you are now following user:{followed_user.username}'}, status=status.HTTP_201_CREATED)
    