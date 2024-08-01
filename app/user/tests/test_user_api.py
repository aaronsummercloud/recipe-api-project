""" Tests for the User api"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# URL for the User app, create method
CREATE_USER_URL = reverse('user:create')

def create_user(**params):
    """ create and return a new user """
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """ Test the public features of the user api """

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """ test creating a user is successful """
        payload = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'name': 'Test Name',
        }

        result = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

        self.assertNotIn('password', result.data)

    def test_user_with_email_exists(self):
        """ tests error returned if user with email exists """
        payload = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'name': 'test user',
        }

        create_user(**payload)

        result = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """ test is password is errored if < 5 chars """
        payload = {
            'email': 'test2@example.com',
            'password': 'pass',
            'name': 'test user',
        }
        
        result = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
