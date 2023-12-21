from django.test import TestCase
from users.models import CustomUser

# Create your tests here.

class UserTestCase(TestCase):

    def test_create_user(self):
        """Test that a user can be created."""

        username='test_user'
        email='test_user@example.com'
        password='password_123'

        user = CustomUser.objects.create_user(username=username, email=email, password=password)
   
        self.assertEqual(user.username, 'test_user')
        self.assertTrue(user.check_password(password))
        self.assertNotEqual(user.password, password)
        self.assertNotEqual(user.password, password)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    
    def test_create_superuser(self):
        user = CustomUser.objects.create_superuser(
            username="admin",
            email="adminuser@example.com",
            password="adminpassword",
        )
        self.assertEqual(user.username, "admin")
        self.assertEqual(user.email, "adminuser@example.com")
        self.assertTrue(user.check_password("adminpassword"))        
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)