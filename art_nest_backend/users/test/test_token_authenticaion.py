from datetime import timedelta
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class TokenAuthenticationTest(APITestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test_user@example.com',
            password='testpassword'
        )

    def test_token_generation(self):
        # Test token generation when a user logs in
        login_url = reverse('users:token_obtain_pair')  # Adjust to your URL configuration
        data = {
            
            'email':'test_user@example.com',
            'password': 'testpassword'
        }

        response = self.client.post(login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_access_to_protected_views(self):
        # Test access to protected views using the generated token
        token = RefreshToken.for_user(self.user)
        token.access_token.set_exp(timedelta(seconds=3600))  # Set token expiration, adjust as needed
        auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

        protected_url = reverse('protected_view')  # Replace with the URL of your protected view
        response = self.client.get(protected_url, **auth_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)