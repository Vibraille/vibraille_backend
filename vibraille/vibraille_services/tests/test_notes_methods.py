from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
import json

from vibraille.vibraille_services.models import User, Note



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
        self.view_all_notes_url = reverse('view_all_notes')

        # Create user for tests
        self.client.post(self.signup_url, self.reg_info)

        # Login
        self.test_user = User.objects.get(username=self.reg_info['username'])
        response = self.client.post(
            self.login_url,
            {'username': self.test_user.username, 'password': self.reg_info['password']}
        )
        self.access_token = response.data['access']

        # Create Note
        self.tst_img = "./vibraille/vibraille_services/tests/image_test.jpg"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        _note_resp = self.client.post(self.translation_url, {
            "img": open(self.tst_img, "rb")
        })
        self.note_data = _note_resp.data

    def test_get_all_notes(self):
        """Test retrieve all notes"""
        response = self.client.get(self.view_all_notes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        _processed_data = json.loads(response.data)
        self.assertTrue(response.data)
        self.assertEqual(
            ['created', 'title', 'img', 'img_name', 'ascii_text', 'braille_format', 'braille_binary', 'user']
            , list(_processed_data[0]['fields'].keys()))
        self.assertEqual(len(_processed_data), 1)

    def test_get_specific_note(self):
        """Test retrieve specific notes"""
        note_id = self.note_data['id']
        response = self.client.get(f'/notes/{note_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        processed_data = json.loads(response.data)
        self.assertTrue(response.data)
        self.assertEqual(
            ['created', 'title', 'img', 'img_name', 'ascii_text', 'braille_format', 'braille_binary', 'user']
            , list(processed_data[0]['fields'].keys()))
        self.assertEqual(len(processed_data), 1)

    def test_get_edit_note(self):
        """Test retrieve specific notes"""
        note_id = self.note_data['id']
        data = {'title': 'new_title'}
        original_title = self.note_data['title']
        response = self.client.put(f'/notes/{note_id}/edit', data)
        processed_data = json.loads(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(processed_data[0]['fields']['title'], data['title'])
        self.assertNotEqual(original_title, processed_data[0]['fields']['title'])

    def test_delete_note(self):
        note_id = self.note_data['id']
        response = self.client.delete(f'/notes/{note_id}/delete')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        follow_response = json.loads(self.client.get(self.view_all_notes_url).data)
        self.assertEqual(len(follow_response), 0)

    def test_invalid_method_get_all(self):
        """Test invalid HTTP method calls."""
        response = self.client.put(self.view_all_notes_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "PUT" not allowed.',
        )
        response = self.client.delete(self.view_all_notes_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "DELETE" not allowed.',
        )
        response = self.client.post(self.view_all_notes_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "POST" not allowed.',
        )

    def test_invalid_method_details_note(self):
        """Test invalid HTTP method calls."""
        note_id = self.note_data['id']
        response = self.client.put(f'/notes/{note_id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "PUT" not allowed.',
        )
        response = self.client.delete(f'/notes/{note_id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "DELETE" not allowed.',
        )
        response = self.client.post(f'/notes/{note_id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "POST" not allowed.',
        )

    def test_invalid_method_edit_note(self):
        """Test invalid HTTP method calls."""
        note_id = self.note_data['id']
        response = self.client.get(f'/notes/{note_id}/edit')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "GET" not allowed.',
        )
        response = self.client.get(f'/notes/{note_id}/edit')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "GET" not allowed.',
        )
        response = self.client.post(f'/notes/{note_id}/edit')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "POST" not allowed.',
        )

    def test_invalid_method_delete_note(self):
        """Test invalid HTTP method calls."""
        note_id = self.note_data['id']
        response = self.client.put(f'/notes/{note_id}/delete')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "PUT" not allowed.',
        )
        response = self.client.get(f'/notes/{note_id}/delete')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "GET" not allowed.',
        )
        response = self.client.post(f'/notes/{note_id}/delete')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            str(response.data['detail']),
            'Method "POST" not allowed.',
        )
