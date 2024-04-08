from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
import json
from .models import CustomUser
from django.test import TestCase
from .views import register_user, login_user, user_details, referrals

base_data = {
    "name": "Base User",
    "email": "base@example.com",
    "password": "base_password"
}

class UserRegistrationTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')

    def test_register_user1(self):
        data = base_data.copy()
        data["name"] = "John Doe"
        data["email"] = "john.doe@example.com"
        data["password"] = "johndoe_password"
        response = self.client.post(self.register_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CustomUser.objects.filter(email=data['email']).exists())

    def test_register_user2(self):
        data = base_data.copy()
        data["name"] = "Jane Smith"
        data["email"] = "jane.smith@example.com"
        data["password"] = "janesmith_password"
        response = self.client.post(self.register_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CustomUser.objects.filter(email=data['email']).exists())
