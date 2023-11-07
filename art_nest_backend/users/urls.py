from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)

app_name='users'


urlpatterns = [    
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('create', views.CreateCustomUserView.as_view(), name='create_a_new_CustomUser'),
    path('<int:pk>', views.RetriveAndUpdateCustomUserView.as_view(), name='retrive_and_update_user_own_info'),
    path('<int:pk>/change-password', views.UpdateUserPasswordView.as_view(), name='change_user_password'),
    path('search', views.SearchUserByUsernameView.as_view(), name='search_users_by_their_usernames'),
]


