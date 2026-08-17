from rest_framework import status

from service_requests.models import ServiceRequest
from incidents.tests.base import BaseAPITestCase


class ServiceRequestAPITests(BaseAPITestCase):

    def setUp(self):
        super().setUp()

        self.authenticate_user(self.admin_user)

        self.service_request = ServiceRequest.objects.create(
            title="Existing laptop access request",
            description=(
                "User requires access to a new laptop."
            ),
            priority="P2",
            status="OPEN",
            requester=self.admin_user,
        )

    def test_admin_can_get_service_request_list(self):

        response = self.client.get(
            "/api/v1/service-requests/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            response.data["success"]
        )

    def test_admin_can_create_service_request(self):

        data = {
            "title": "New software installation",
            "description": (
                "Install approved development software."
            ),
            "priority": "P2",
            "status": "OPEN",
        }

        response = self.client.post(
            "/api/v1/service-requests/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            response.data["success"]
        )

        self.assertTrue(
            ServiceRequest.objects.filter(
                title="New software installation"
            ).exists()
        )

    def test_admin_can_get_service_request_detail(self):

        response = self.client.get(
            f"/api/v1/service-requests/"
            f"{self.service_request.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["data"]["id"],
            self.service_request.id
        )

    def test_admin_can_put_service_request(self):

        data = {
            "title": "Updated laptop access request",
            "description": (
                "Updated description for the request."
            ),
            "priority": "P1",
            "status": "IN_PROGRESS",
        }

        response = self.client.put(
            f"/api/v1/service-requests/"
            f"{self.service_request.id}/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.service_request.refresh_from_db()

        self.assertEqual(
            self.service_request.title,
            "Updated laptop access request"
        )

    def test_admin_can_patch_service_request(self):

        response = self.client.patch(
            f"/api/v1/service-requests/"
            f"{self.service_request.id}/",
            {
                "priority": "P1"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.service_request.refresh_from_db()

        self.assertEqual(
            self.service_request.priority,
            "P1"
        )

    def test_admin_can_delete_service_request(self):

        request_id = self.service_request.id

        response = self.client.delete(
            f"/api/v1/service-requests/"
            f"{request_id}/"
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_200_OK,
                status.HTTP_204_NO_CONTENT,
            ]
        )

        self.assertFalse(
            ServiceRequest.objects.filter(
                id=request_id
            ).exists()
        )