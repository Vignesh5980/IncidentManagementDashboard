from rest_framework import status

from accounts.models import CustomUser
from incidents.models import Incident
from .base import BaseAPITestCase


class IncidentPermissionTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()

        self.other_support_engineer = (
            CustomUser.objects.create_user(
                username="support_test_2",
                password="TestPassword123",
                role="SUPPORT_ENGINEER",
            )
        )

        self.assigned_incident = Incident.objects.create(
            title="Assigned application issue",
            description=(
                "This incident is assigned to the "
                "support engineer."
            ),
            priority="P2",
            status="OPEN",
            application="Customer Portal",
            created_by=self.admin_user,
            assigned_to=self.support_engineer,
        )

        self.other_incident = Incident.objects.create(
            title="Another application issue",
            description=(
                "This incident belongs to another "
                "support engineer."
            ),
            priority="P3",
            status="OPEN",
            application="Customer Portal",
            created_by=self.admin_user,
            assigned_to=self.other_support_engineer,
        )

    # ==============================
    # ADMIN TESTS
    # ==============================

    def test_admin_can_get_incidents(self):

        self.authenticate_user(self.admin_user)

        response = self.client.get(
            "/api/v1/incidents/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_can_create_incident(self):

        self.authenticate_user(self.admin_user)

        data = {
            "title": "Admin created incident",
            "description": (
                "Incident created by the admin user."
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
            status.HTTP_201_CREATED
        )

    def test_admin_can_update_incident(self):

        self.authenticate_user(self.admin_user)

        response = self.client.patch(
            f"/api/v1/incidents/"
            f"{self.assigned_incident.id}/",
            {
                "priority": "P1"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_can_delete_incident(self):

        self.authenticate_user(self.admin_user)

        response = self.client.delete(
            f"/api/v1/incidents/"
            f"{self.assigned_incident.id}/"
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_204_NO_CONTENT,
            ]
        )

    # ==============================
    # TEAM LEAD TESTS
    # ==============================

    def test_team_lead_can_get_incidents(self):

        self.authenticate_user(self.team_lead)

        response = self.client.get(
            "/api/v1/incidents/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_team_lead_can_create_incident(self):

        self.authenticate_user(self.team_lead)

        data = {
            "title": "Team Lead created incident",
            "description": (
                "Incident created by the team lead."
            ),
            "priority": "P2",
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
            status.HTTP_201_CREATED
        )

    def test_team_lead_can_update_incident(self):

        self.authenticate_user(self.team_lead)

        response = self.client.patch(
            f"/api/v1/incidents/"
            f"{self.assigned_incident.id}/",
            {
                "priority": "P1"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_team_lead_cannot_delete_incident(self):

        self.authenticate_user(self.team_lead)

        response = self.client.delete(
            f"/api/v1/incidents/"
            f"{self.assigned_incident.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # ==============================
    # SUPPORT ENGINEER TESTS
    # ==============================

    def test_support_engineer_can_get_incidents(self):

        self.authenticate_user(
            self.support_engineer
        )

        response = self.client.get(
            "/api/v1/incidents/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_support_engineer_can_create_incident(self):

        self.authenticate_user(
            self.support_engineer
        )

        data = {
            "title": "Support engineer incident",
            "description": (
                "Incident reported by a support engineer."
            ),
            "priority": "P3",
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
            status.HTTP_201_CREATED
        )

    def test_support_engineer_can_update_assigned_incident(self):

        self.authenticate_user(
            self.support_engineer
        )

        response = self.client.patch(
            f"/api/v1/incidents/"
            f"{self.assigned_incident.id}/",
            {
                "priority": "P1"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_support_engineer_cannot_update_other_incident(self):

        self.authenticate_user(
            self.support_engineer
        )

        response = self.client.patch(
            f"/api/v1/incidents/"
            f"{self.other_incident.id}/",
            {
                "priority": "P1"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_support_engineer_cannot_delete_incident(self):

        self.authenticate_user(
            self.support_engineer
        )

        response = self.client.delete(
            f"/api/v1/incidents/"
            f"{self.assigned_incident.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )