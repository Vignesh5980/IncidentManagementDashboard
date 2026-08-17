from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser


class JWTAuthenticationTests(APITestCase):

    def setUp(self):

        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="TestPassword123",
            role="ADMIN",
        )

    def test_user_can_obtain_jwt_token(self):

        response = self.client.post(
            "/api/v1/auth/token/",
            {
                "username": "testuser",
                "password": "TestPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

        self.assertIn(
            "refresh",
            response.data,
        )

    def test_invalid_credentials_fail(self):

        response = self.client.post(
            "/api/v1/auth/token/",
            {
                "username": "testuser",
                "password": "WrongPassword",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )