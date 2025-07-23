from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from .models import User


class EmailVerificationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create user with valid token (created now)
        self.valid_user = User.objects.create_user(
            email='valid@example.com',
            password='validpass123',
            is_active=False,
            is_verified=False
        )
        self.valid_user.verification_token = 'valid-token'
        self.valid_user.verification_token_created_at = timezone.now()
        self.valid_user.save()
        
        # Create user with expired token (created 25 hours ago)
        self.expired_user = User.objects.create_user(
            email='expired@example.com',
            password='expiredpass123',
            is_active=False,
            is_verified=False
        )
        self.expired_user.verification_token = 'expired-token'
        self.expired_user.verification_token_created_at = timezone.now() - timedelta(hours=25)
        self.expired_user.save()

    def test_successful_verification(self):
        """Test verifying email with valid token"""
        url = reverse('user-verify-email') + '?token=valid-token'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Email successfully verified')
        
        # Refresh user from db
        self.valid_user.refresh_from_db()
        self.assertTrue(self.valid_user.is_verified)
        self.assertTrue(self.valid_user.is_active)
        self.assertIsNone(self.valid_user.verification_token)
        self.assertIsNone(self.valid_user.verification_token_created_at)

    def test_expired_token(self):
        """Test verifying with expired token"""
        url = reverse('user-verify-email') + '?token=expired-token'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Verification link has expired')
        
        # Refresh user from db
        self.expired_user.refresh_from_db()
        self.assertFalse(self.expired_user.is_verified)
        self.assertFalse(self.expired_user.is_active)
        self.assertIsNone(self.expired_user.verification_token)
        self.assertIsNone(self.expired_user.verification_token_created_at)

    def test_invalid_token(self):
        """Test verifying with invalid token"""
        url = reverse('user-verify-email') + '?token=invalid-token'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid verification token')

    def test_missing_token(self):
        """Test verifying without token"""
        url = reverse('user-verify-email')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Token is required')