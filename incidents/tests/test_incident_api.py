from rest_framework import status

from incidents.models import Incident
from .base import BaseAPITestCase


class IncidentAPITests(BaseAPITestCase):

    def setUp(self):
        super().setUp()

        self.authenticate_user(
            self.admin_user
        )

        self.incident_data = {
            "title": "Production database failure",
            "description": (
                "Users cannot connect to the "
                "production database."
            ),
            "priority": "P1",
            "status": "OPEN",
            "application": "Customer Portal",
        }

        self.incident = Incident.objects.create(
            title="Existing application issue",
            description=(
                "An existing incident for "
                "testing purposes."
            ),
            priority="P2",
            status="OPEN",
            application="Customer Portal",
            created_by=self.admin_user,
        )

    def test_admin_can_get_incident_list(self):

        response = self.client.get(
            "/api/v1/incidents/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            response.data["success"]
        )

        self.assertEqual(
            response.data["status_code"],
            200
        )

    def test_admin_can_create_incident(self):

        response = self.client.post(
            "/api/v1/incidents/",
            self.incident_data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            response.data["success"]
        )

        self.assertEqual(
            response.data["status_code"],
            201
        )

        self.assertEqual(
            response.data["data"]["title"],
            "Production database failure"
        )

        self.assertTrue(
            Incident.objects.filter(
                title="Production database failure"
            ).exists()
        )

    def test_admin_can_get_incident_detail(self):

        response = self.client.get(
            f"/api/v1/incidents/{self.incident.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            response.data["success"]
        )

        self.assertEqual(
            response.data["data"]["id"],
            self.incident.id
        )


    def test_admin_can_update_incident(self):

        response = self.client.patch(
            f"/api/v1/incidents/{self.incident.id}/",
            {
                "priority": "P1"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            response.data["success"]
        )

        self.incident.refresh_from_db()

        self.assertEqual(
            self.incident.priority,
            "P1"
        )

    def test_admin_can_delete_incident(self):

        response = self.client.delete(
            f"/api/v1/incidents/{self.incident.id}/"
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_204_NO_CONTENT,
            ]
        )

        self.incident.refresh_from_db()

        self.assertTrue(
            self.incident.is_deleted
        )