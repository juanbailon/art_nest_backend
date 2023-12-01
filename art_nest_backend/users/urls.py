from django.urls import path
from . import views


app_name='users'


urlpatterns = [    
    path('create', views.CreateCustomUserView.as_view(), name='create_a_new_CustomUser'),
    path('<str:username>/', views.RetriveUpdateAndDeleteCustomUserView.as_view(), name='retrive_and_update_user_own_info'),
    path('<str:username>/change-password', views.UpdateUserPasswordView.as_view(), name='change_user_password'),
    path('search', views.SearchUserByUsernameView.as_view(), name='search_users_by_their_usernames'),
    path('avatars', views.ListAllAvatarsView.as_view(), name='lists_all_the_available_avatars'),
    path('<str:username>/avatar', views.UserAvartarView.as_view(), name='assings_an_avatar_to_the_user'),
    path('<str:username>/profile/picture', views.ProfilePictureView.as_view(), name='assings_a_profile_picture_to_the_user'),
    path('get-id', views.GetCustomUserID.as_view(), name='get_the_related_id_to_the_user'),

]

