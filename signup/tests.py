from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class RegistrationTests(TestCase):
    def test_registration_form(self):
        user_data = {
            'first_name': 'Zahra',
            'last_name': 'Ebrahimi',
            'phone': '09123456789',
            'email': 'zahra@gmail.com',
            'password1': 'Password123',
            'password2': 'Password123',
        }

        response = self.client.post(reverse('signup'), data=user_data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(email='zahra@gmail.com').exists())

    def test_registration_form_with_null_team(self):

        user_data = {
            'first_name': 'Zahra',
            'last_name': 'Ebrahimi',
            'phone': '09123456789',
            'email': 'zahra@gmail.com',
            'password1': 'Password123',
            'password2': 'Password123',
            'team': 'None',
        }

        response = self.client.post(reverse('signup'), data=user_data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(email='zahra@gmail.com').exists())

