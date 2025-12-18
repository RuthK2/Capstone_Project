from rest_framework.test import APITestCase
from django.contrib.auth.models import User 
from rest_framework import status
from django.urls import reverse


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.test_username = 'testuser'
        self.test_email = 'test@example.com'
        self.test_password = 'testpass123'
        self.user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password)

    def test_user_registration_valid(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
    
    def test_user_registration_password_mismatch(self):
        url = reverse('register')
        data = {
            'username': 'invaliduser',
            'email': 'invalid@example.com',
            'password': 'pass123',
            'password2': 'differentpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_user_registration_existing_username(self):
        url = reverse('register')
        data = {
            'username': self.test_username,
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_user_login_valid(self):
        url = reverse('login')
        data = {'username': self.test_username, 'password': self.test_password}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_login_invalid(self):
        url = reverse('login')
        data = {'username': 'invaliduser', 'password': 'wrongpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid credentials')
    
    def test_logout(self):
        url = reverse('logout')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logout successful')
    
    # Test without authentication
    def test_protected_endpoint_no_token(self):
        url = reverse('protected')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Authentication credentials were not provided.')

    # Test with authentication
    def test_protected_endpoint_with_token(self):
        url = reverse('protected')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'This is a protected endpoint')


