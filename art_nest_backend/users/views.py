from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from .serializers import CustomUserSerializer, UpdateCustomUserSerializer, PasswordUpdateSerializer, SearchUsernameSerializer
from .models import CustomUser
from rest_framework_simplejwt.views import TokenRefreshView
from .permissions import IsProfileOwnerPermission
from .filters import UsernameFilter, filters


# Create your views here.


class CreateCustomUserView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]


class RetriveAndUpdateCustomUserView(generics.RetrieveUpdateAPIView):
    """ 
    This view lets the users consult and update his own data, in the updates the user 
    can NOT change the password, since this is consider a critical task and therefor is
    assing to an especific endpoint
    """
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsProfileOwnerPermission]
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CustomUserSerializer
        elif self.request.method in ('PUT', 'PATCH'):
            return UpdateCustomUserSerializer


class UpdateUserPasswordView(generics.UpdateAPIView):
    """ this view updates the user password, this change can only be done through a PUT, NOT a PATCH """
    
    serializer_class =  PasswordUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileOwnerPermission]
    queryset = CustomUser.objects.all()
    lookup_field = 'pk'

    http_method_names = ['put'] # thsi makes only the PUT available and the PATCH inavailabe

    def put(self, request, *args, **kwargs):

        serializer = self.get_serializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        
        new_password = serializer.validated_data['new_password']
        user = request.user
        user.set_password(new_password)
        user.save()

        return Response("Password updated successfully", status=status.HTTP_200_OK)
    

class SearchUserByUsernameView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SearchUsernameSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = UsernameFilter
