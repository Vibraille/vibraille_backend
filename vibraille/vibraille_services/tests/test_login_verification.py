from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from vibraille.vibraille_services.models import User


class LoginTestCase(APITestCase):

    def setUp(self):
        self.reg_info = {
            'username': 'test_user',
            'password': 'test_Pass',
            'phone_number': '+1(123)456-7890',
            'email': 'test_user@test.com'
        }
        self.client = APIClient()
        self.signup_url = reverse('register')
        self.login_url = reverse('login')
        self.login_refresh_url = reverse('login_token_refresh')
        self.verify_phone_url = reverse('verify_phone')
        self.verify_email_url = reverse('verify_email')

        # Create user for tests
        response = self.client.post(self.signup_url, self.reg_info)
        self.test_user = User.objects.get(username=self.reg_info['username'])
        self.verification_phone_str = response.data['verification_strings']['verify_phone']
        self.verification_email_str = response.data['verification_strings']['verify_email']

    def test_login_with_username(self):
        """Test with basic username."""
        login_data = {'username': self.reg_info['username'], 'password': self.reg_info['password']}
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])
        self.assertEqual(response.data['user']['email'], self.test_user.email)
        self.assertEqual(response.data['user']['username'], self.test_user.username)
        self.assertEqual(response.data['user']['id'], self.test_user.id)
        self.assertEqual(response.data['user']['phone_number'], self.test_user.vibrailleuser.phone_number)

    def test_login_failure(self):
        """Test failure."""
        login_data = {'username': 'potato', 'password': self.reg_info['password']}
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            str(response.data['detail']),
            'No active account found with the given credentials',
        )

    def test_invalid_method_login(self):
        login_data = {'username': self.reg_info['username'], 'password': self.reg_info['password']}
        response = self.client.delete(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "DELETE" not allowed.',
        )
        response = self.client.put(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "PUT" not allowed.',
        )
        response = self.client.get(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "GET" not allowed.',
        )

    def test_verification_login(self):
        """Tests login without verification, phone verification, and email verification."""
        # Test failures because devices not verified
        login_data = {'email': self.reg_info['email'], 'password': self.reg_info['password']}
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(
            str(response.data),
            'Email is not verified yet!',
        )
        login_data = {'phone_number': self.reg_info['phone_number'], 'password': self.reg_info['password']}
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(
            str(response.data),
            'Phone Number is not verified yet!',
        )

        # Test email verification and login
        verification_data = {'email': self.reg_info['email'], 'verify_str': self.verification_email_str}
        self.client.put(self.verify_email_url, verification_data)
        login_data = {'email': self.reg_info['email'], 'password': self.reg_info['password']}
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])
        self.assertEqual(response.data['user']['email'], self.test_user.email)
        self.assertEqual(response.data['user']['username'], self.test_user.username)
        self.assertEqual(response.data['user']['id'], self.test_user.id)
        self.assertEqual(response.data['user']['phone_number'], self.test_user.vibrailleuser.phone_number)

        # Test phone verification and login
        verification_data = {'phone_number': self.reg_info['phone_number'], 'verify_str': self.verification_phone_str}
        self.client.put(self.verify_phone_url, verification_data)
        login_data = {'phone_number': self.reg_info['phone_number'], 'password': self.reg_info['password']}
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])
        self.assertEqual(response.data['user']['email'], self.test_user.email)
        self.assertEqual(response.data['user']['username'], self.test_user.username)
        self.assertEqual(response.data['user']['id'], self.test_user.id)
        self.assertEqual(response.data['user']['phone_number'], self.test_user.vibrailleuser.phone_number)