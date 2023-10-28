from django.db import models
from users.models import CustomUser

# Create your models here.

class Follow(models.Model):

    follower_user_id = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)
    following_user_id = models.ForeignKey(CustomUser, null=False, blank=False, on_delete=models.CASCADE)

