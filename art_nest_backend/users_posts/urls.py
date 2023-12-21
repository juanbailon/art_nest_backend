from django.urls import path
from . import views


app_name='users_posts'


urlpatterns = [    
    path('<str:username>/post', views.CreateUserPostView.as_view(), name='greet'),

]