from django.urls import path
from . import views


app_name='users_posts'


urlpatterns = [    
    path('<str:username>/post', views.CreateUserPostView.as_view(), name='create_post'),
    path('<str:username>/feed', views.UserFeedView.as_view(), name='get_user_feed'),

]