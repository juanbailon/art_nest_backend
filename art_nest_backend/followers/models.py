from django.db import models
from users.models import CustomUser

# Create your models here.

class Follow(models.Model):
    """ 
    since the fields  follower and followed both reference the CustomUser model, we have to provide a related_name
    for them so that django can create the reverse relationship to the CustomUser model, because otherwise we will
    get an error.

    So in the case we have an instance of the CustomUser model, lets call this instance my_user.
    Then if we want to get all the followers that my_user has, we can do:

        my_user.follower_users 
        
        This will give us all the rows of the Follow table where my_user is in the  followed column. 

    If we need the user that my_user follows then we can get all the row of the Follow table where 
    my_user is in the follower column by doing

        my_user.followed_users

    """

    follower = models.ForeignKey(CustomUser, related_name='followed_users', null=False, blank=False, on_delete=models.CASCADE)
    followed = models.ForeignKey(CustomUser, related_name='follower_users', null=False, blank=False, on_delete=models.CASCADE)

