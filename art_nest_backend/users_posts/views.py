from rest_framework.views import APIView
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from users.permissions import IsProfileOwnerPermission
from .serializers import UserPostSerializer

# Create your views here.

class CreateUserPostView(generics.CreateAPIView):
    serializer_class = UserPostSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileOwnerPermission]

    def create(self, request, *args, **kwargs):
        # Access the value of the 'username' path parameter
        username = kwargs.get('username')

        request.data['user'] = request.user.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        data = serializer.data
        data.pop('user')
        data['username'] = username

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)