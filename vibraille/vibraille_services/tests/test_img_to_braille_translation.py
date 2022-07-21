from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from vibraille.vibraille_services.models import User



class ImageTranslationTestCase(APITestCase):

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
        self.translation_url = reverse('translate_img')

        # Create user for tests
        self.client.post(self.signup_url, self.reg_info)
        self.test_user = User.objects.get(username=self.reg_info['username'])
        response = self.client.post(
            self.login_url,
            {'username': self.test_user.username, 'password': self.reg_info['password']}
        )
        self.access_token = response.data['access']
        self.tst_img = "./vibraille/vibraille_services/tests/image_test.jpg"


    def test_translation(self):
        """Test image to braille translation."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(self.translation_url, {
            "img": open(self.tst_img, "rb")
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.test_user.id)
        self.assertEqual(response.data['title'], 'image_test.jpg')
        self.assertEqual(response.data['img'], 'http://testserver/media/image_test.jpg')
        self.assertEqual(response.data['img_name'], 'image_test.jpg')
        self.assertTrue(response.data['ascii_text'])
        self.assertEqual(
            response.data['braille_format'],
            '⠧⠀⠂⠂⠀⠍⠁⠗⠉⠓⠀⠒⠎⠀⠛⠙⠀⠇⠁⠺⠀⠓⠕⠺⠀⠁⠃⠕⠥⠞⠀⠏⠑⠕⠏⠇⠑⠀⠃⠑⠊⠀⠉⠁⠗⠞⠕⠕⠝⠊⠵⠑⠙⠹⠀⠎⠑⠑⠀⠏⠁⠛⠑⠀⠒⠂'
        )
        self.assertEqual(
            response.data['braille_binary'],
            '1110010000000100000100000000001011001000001110101001001100100000000100100111'
            '0000000011011010011000000011100010000001011100000011001010101001011100000010'
            '0000110000101010101001011110000000111100100010101010111100111000100010000000'
            '1100001000100101000000001001001000001110100111101010101010101011100101001010'
            '11100010100110100111000000011100100010100010000000111100100000110110100010000'
            '000010010010000'
        )

    def test_invalid_method_submission(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.put(self.translation_url, {
            "img": open(self.tst_img, "rb")
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "PUT" not allowed.',
        )
        response = self.client.get(self.translation_url, {
            "img": open(self.tst_img, "rb")
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "GET" not allowed.',
        )
        response = self.client.delete(self.translation_url, {
            "img": open(self.tst_img, "rb")
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "DELETE" not allowed.',
        )

