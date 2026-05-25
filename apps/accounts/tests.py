from django.test import TestCase
from apps.accounts.models import User


class UserModelTest(TestCase):
    """Tests for the User model"""
    
    def test_create_user(self):
        """Test creating a user with email, username and password"""
        user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpass'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('testpass'))
        self.assertEqual(user.role, 'user')  # Default role
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_admin())
    
    def test_user_roles(self):
        """Test user role methods"""
        user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='pass'
        )
        self.assertFalse(user.is_admin())
        self.assertFalse(user.is_moderator())
        
        # Test moderator
        moderator = User.objects.create_user(
            email='mod@example.com',
            username='moderator',
            password='pass',
            role='moderator'
        )
        self.assertTrue(moderator.is_moderator())
        self.assertFalse(moderator.is_admin())
        
        # Test admin
        admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='pass',
            role='admin'
        )
        self.assertTrue(admin.is_admin())
        self.assertTrue(admin.is_moderator())  # Admins have moderator permissions
