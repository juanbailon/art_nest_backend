from django.db import models
from users.models import CustomUser
# Create your models here.

class UserPost(models.Model):
    post_image = models.ImageField(null=False, upload_to='users_posts/')
    user = models.OneToOneField(CustomUser, on_delete=  models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=False)