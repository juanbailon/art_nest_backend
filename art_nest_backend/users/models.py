from django.core import validators
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        # Create and save a new user with the given email and password
        validate_password(password)
        
        user = self.model(username= username, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()   
        
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        # Create and save a new superuser with the given email and password
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True

        user = self.create_user(username=username,
                                email=email,
                                password=password,
                                **extra_fields
                                )
        
        return user


class CustomUser(AbstractUser, PermissionsMixin):

    first_name = None
    last_name = None
    username = models.CharField(max_length=30, unique=True, blank=False, null=False)    
    email = models.EmailField(unique=True, blank=False, null=False) 
    password = models.CharField(max_length=200, validators=[validators.MinLengthValidator(8)])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    
    USERNAME_FIELD = "email"
    #password is always required by default
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return f'user email: {self.email} \n username:{self.username}'


