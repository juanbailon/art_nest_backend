from django_filters import rest_framework as filters
from .models import CustomUser

class UsernameFilter(filters.FilterSet):
    """
    FilterSet for searching users by username.

    Filters:
    - `username`: Case-insensitive partial match filter for usernames.
    """
    
    username = filters.CharFilter(field_name='username', lookup_expr='icontains')

    class Meta:
        model = CustomUser
        fields = ['username']
