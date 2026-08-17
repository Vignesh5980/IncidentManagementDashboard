from rest_framework.test import APITestCase

from accounts.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

class BaseAPITestCase(APITestCase):

    def setUp(self):

        self.admin_user = CustomUser.objects.create_user(
            username="admin_test",
            password="TestPassword123",
            role="ADMIN",
        )

        self.team_lead = CustomUser.objects.create_user(
            username="teamlead_test",
            password="TestPassword123",
            role="TEAM_LEAD",
        )

        self.support_engineer = CustomUser.objects.create_user(
            username="support_test",
            password="TestPassword123",
            role="SUPPORT_ENGINEER",
        )
    def authenticate_user(self, user):

        refresh = RefreshToken.for_user(user)

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {refresh.access_token}"
            )
        )