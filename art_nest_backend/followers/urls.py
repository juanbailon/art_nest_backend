from django.urls import path
from . import views

app_name='followers'


urlpatterns = [    
    path('<int:pk>', views.FollowNewUserView.as_view(), name='follow_a_new_user_by_id'),
    # path('v', views.FollowNewUserView2.as_view(), name='follow_a_new_user2'),
    path('<str:pk>', views.FollowNewUserView.as_view(), name='follow_a_new_user_by_username'),
]
