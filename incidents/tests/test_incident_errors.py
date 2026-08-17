from django.core.cache import cache

from rest_framework import status

from incidents.models import Incident
from .base import BaseAPITestCase


class IncidentErrorTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()

        cache.clear()

        self.incident = Incident.objects.create(
            title="Existing test incident",
            description=(
                "Incident created for error "
                "response testing."
            ),
            priority="P2",
            status="OPEN",
            application="Customer Portal",
            created_by=self.admin_user,
            assigned_to=self.support_engineer,
        )

    def test_empty_title_returns_validation_error(self):

        self.authenticate_user(self.admin_user)

        data = {
            "title": "",
            "description": (
                "Testing validation for an empty title."
            ),
            "priority": "P1",
            "status": "OPEN",
            "application": "Customer Portal",
        }

        response = self.client.post(
            "/api/v1/incidents/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertFalse(response.data["success"])

        self.assertEqual(
            response.data["status_code"],
            400
        )

        self.assertEqual(
            response.data["message"],
            "Validation failed."
        )

        self.assertIn(
            "title",
            response.data["errors"]
        )

    def test_invalid_priority_returns_validation_error(self):

        self.authenticate_user(self.admin_user)

        data = {
            "title": "Invalid priority test incident",
            "description": (
                "Testing invalid priority validation."
            ),
            "priority": "P10",
            "status": "OPEN",
            "application": "Customer Portal",
        }

        response = self.client.post(
            "/api/v1/incidents/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertFalse(response.data["success"])

        self.assertEqual(
            response.data["status_code"],
            400
        )

        self.assertIn(
            "priority",
            response.data["errors"]
        )

    def test_missing_jwt_returns_401(self):

        self.client.credentials()

        response = self.client.get(
            "/api/v1/incidents/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        self.assertFalse(response.data["success"])

        self.assertEqual(
            response.data["status_code"],
            401
        )

        self.assertIn(
            "message",
            response.data
        )

        self.assertIn(
            "errors",
            response.data
        )

    def test_invalid_jwt_returns_401(self):

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                "Bearer invalid.jwt.token"
            )
        )

        response = self.client.get(
            "/api/v1/incidents/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        self.assertFalse(response.data["success"])

        self.assertEqual(
            response.data["status_code"],
            401
        )

        self.assertIn(
            "errors",
            response.data
        )

    def test_support_engineer_delete_returns_403(self):

        self.authenticate_user(
            self.support_engineer
        )

        response = self.client.delete(
            f"/api/v1/incidents/"
            f"{self.incident.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertFalse(response.data["success"])

        self.assertEqual(
            response.data["status_code"],
            403
        )

        self.assertIn(
            "message",
            response.data
        )

        self.assertIn(
            "errors",
            response.data
        )

    def test_nonexistent_incident_returns_404(self):

        self.authenticate_user(
            self.admin_user
        )

        response = self.client.get(
            "/api/v1/incidents/999999/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertFalse(response.data["success"])

        self.assertEqual(
            response.data["status_code"],
            404
        )

        self.assertIn(
            "message",
            response.data
        )

        self.assertIn(
            "errors",
            response.data
        )

    def test_invalid_status_transition_returns_400(self):

        self.authenticate_user(
            self.admin_user
        )

        resolved_incident = Incident.objects.create(
            title="Resolved incident test",
            description=(
                "Testing invalid status transition."
            ),
            priority="P2",
            status="RESOLVED",
            application="Customer Portal",
            created_by=self.admin_user,
            assigned_to=self.support_engineer,
        )

        response = self.client.patch(
            f"/api/v1/incidents/"
            f"{resolved_incident.id}/",
            {
                "status": "IN_PROGRESS"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertFalse(response.data["success"])

        self.assertIn(
            "status",
            response.data["errors"]
        )

    def test_rate_limit_is_configured(self):

        from django.conf import settings

        rates = settings.REST_FRAMEWORK.get(
            "DEFAULT_THROTTLE_RATES",
            {}
        )

        self.assertIn(
            "user",
            rates
        )

        self.assertEqual(
            rates["user"],
            "100/hour"
        )