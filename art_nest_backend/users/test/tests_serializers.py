from django.test import TestCase
from unittest import mock
from rest_framework import serializers
from users.models import CustomUser
from users.serializers import CustomUserSerializer


class CustomUserSerializerTestCase(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='test_user',
            email='test_user@example.com',
            password='password'
        )

    def test_create(self):
        serializer = CustomUserSerializer(data={
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'new_password'
        })

        self.assertTrue(serializer.is_valid())

    
        serializer.save()


        # Assert that the user was saved with the correct username and email address.
        user = CustomUser.objects.get(username='new_user')
        self.assertEqual(user.email, 'new_user@example.com')

        # Assert that the serializer data is correct.
        self.assertEqual(serializer.data['username'], 'new_user')
        self.assertEqual(serializer.data['email'], 'new_user@example.com')