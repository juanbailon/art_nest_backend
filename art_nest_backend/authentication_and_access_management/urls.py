from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)

app_name='authentication_and_access_management'


urlpatterns = [    
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('forgot-password/send/email', views.SendForgotPasswordEmailView.as_view(), name='send_forgot_password_email'),
    path('forgot-password/validate/email/otp', views.ValidateForgotPasswordEmailOTPView.as_view(), name='validates_that_the_email_otp_is_valid'),
    path('forgot-password/set-new-password', views.SetNewUserPasswordView.as_view(), name='set_a_new_user_password'),
]
