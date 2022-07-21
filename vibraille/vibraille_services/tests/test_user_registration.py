from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from vibraille.vibraille_services.models import User, VibrailleUser


class UserRegistrationTestCase(APITestCase):

    def setUp(self):
        self.reg_info = {
            'username': 'test_user',
            'password': 'test_Pass',
            'phone_number': '+1(123)456-7890',
            'email': 'test_user@test.com'
        }
        self.client = APIClient()
        self.signup_url = reverse('register')
        self.verification_refresh_url = reverse('verify_refresh')

    def test_full_user_registration(self):
        """Test full user registration."""
        response = self.client.post(self.signup_url, self.reg_info)
        test_user = User.objects.get(username=self.reg_info['username'])
        _vb_user = VibrailleUser.objects.get(user=test_user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(test_user.username, self.reg_info['username'])
        self.assertEqual(test_user.email, self.reg_info['email'])
        self.assertEqual(test_user.vibrailleuser.phone_number, self.reg_info['phone_number'])

        self.assertTrue(test_user.vibrailleuser)
        self.assertEqual(_vb_user.phone_number, self.reg_info['phone_number'])

    def test_verification_str_refresh(self):
        """Test full user registration."""
        response = self.client.post(self.signup_url, self.reg_info)
        test_user = User.objects.get(username=self.reg_info['username'])
        _vb_user = VibrailleUser.objects.get(user=test_user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(_vb_user.veri_str_phone)
        self.assertTrue(_vb_user.veri_str_email)

        _original_veristr_phone = _vb_user.veri_str_phone
        _original_veristr_email = _vb_user.veri_str_email

        resp_phone = self.client.put(
            self.verification_refresh_url,
            {'phone_number': self.reg_info['phone_number']}
        )
        self.assertIsNot(resp_phone.data['verification_phone'], _original_veristr_phone)

        resp_email = self.client.put(
            self.verification_refresh_url,
            {'email': self.reg_info['email']}
        )
        self.assertIsNot(resp_email.data['verification_email'], _original_veristr_email)

    def test_if_user_already_exists(self):
        """Test registration if user already exists."""
        _setup_resp = self.client.post(self.signup_url, self.reg_info)
        response = self.client.post(self.signup_url, self.reg_info)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['username'][0]),
            'A user with that username already exists.',
        )

    def test_invalid_method_registration(self):
        """Test invalid HTTP method calls."""
        response = self.client.put(self.signup_url, self.reg_info)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "PUT" not allowed.',
        )
        response = self.client.delete(self.signup_url, self.reg_info)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "DELETE" not allowed.',
        )
        response = self.client.get(self.signup_url, self.reg_info)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "GET" not allowed.',
        )