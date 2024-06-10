from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User
from rest_framework.authtoken.models import Token

class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register_user')
        self.valid_payload = {
            'email': 'testuser@example.com',
            'password': 'TestPassword!123',
        }
        self.invalid_payload = {
            'email': 'testuser@example.com',
            'password': 'short',
        }

    def test_register_user_with_valid_payload(self):
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(email=self.valid_payload['email']).exists())
        user = User.objects.get(email=self.valid_payload['email'])
        self.assertTrue(user.check_password(self.valid_payload['password']))

    def test_register_user_with_invalid_payload(self):
        response = self.client.post(self.register_url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=self.invalid_payload['email']).exists())

    def test_register_user_with_missing_field(self):
        payload = {'email': 'testuser@example.com'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=payload['email']).exists())

    def test_register_user_with_existing_email(self):
        self.client.post(self.register_url, self.valid_payload, format='json')
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(email=self.valid_payload['email'])
        self.assertEqual(users.count(), 1)
