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
            category="Hardware",
            subcategory="Laptop",
            priority="P2",
            status="SUBMITTED",
            requester=self.admin_user,
        )

    def test_admin_can_get_service_request_list(self):

        response = self.client.get(
            "/api/v1/service-requests/"
        )
        print("LIST STATUS:", response.status_code)
        print("LIST DATA:", response.data)

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
            "category": "Software",
            "subcategory": "Installation",
            "priority": "P2",
            "status": "SUBMITTED",
        }

        response = self.client.post(
            "/api/v1/service-requests/",
            data,
            format="json"
        )

        print("CREATE STATUS:", response.status_code)
        print("CREATE DATA:", response.data)

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
        print("DETAIL STATUS:", response.status_code)
        print("DETAIL DATA:", response.data)

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
            "category": "Hardware",
            "subcategory": "Laptop",
            "priority": "P1",
            "status": "IN_PROGRESS",
        }

        response = self.client.put(
            f"/api/v1/service-requests/"
            f"{self.service_request.id}/",
            data,
            format="json"
        )

        print("PUT STATUS:", response.status_code)
        print("PUT DATA:", response.data)

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

    def test_admin_can_assign_service_request(self):

        response = self.client.patch(
            f"/api/v1/service-requests/"
            f"{self.service_request.id}/assign/",
            {
                "assigned_to": self.support_engineer.id
            },
            format="json"
        )

        print(
            "ADMIN ASSIGN STATUS:",
            response.status_code
        )
        print(
            "ADMIN ASSIGN DATA:",
            response.data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            response.data["success"]
        )

        self.service_request.refresh_from_db()

        self.assertEqual(
            self.service_request.assigned_to_id,
            self.support_engineer.id
        )

    def test_team_lead_can_assign_service_request(self):

        self.authenticate_user(
            self.team_lead
        )

        response = self.client.patch(
            f"/api/v1/service-requests/"
            f"{self.service_request.id}/assign/",
            {
                "assigned_to": self.support_engineer.id
            },
            format="json"
        )

        print(
            "TEAM LEAD ASSIGN STATUS:",
            response.status_code
        )
        print(
            "TEAM LEAD ASSIGN DATA:",
            response.data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            response.data["success"]
        )

        self.service_request.refresh_from_db()

        self.assertEqual(
            self.service_request.assigned_to_id,
            self.support_engineer.id
        )

    def test_support_engineer_cannot_assign_service_request(self):

        self.authenticate_user(
            self.support_engineer
        )

        response = self.client.patch(
            f"/api/v1/service-requests/"
            f"{self.service_request.id}/assign/",
            {
                "assigned_to": self.admin_user.id
            },
            format="json"
        )

        print(
            "SUPPORT ASSIGN STATUS:",
            response.status_code
        )
        print(
            "SUPPORT ASSIGN DATA:",
            response.data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertEqual(
            response.data["detail"],
            "You do not have permission to assign requests."
        )

    def test_assign_service_request_without_assigned_to(self):

        response = self.client.patch(
            f"/api/v1/service-requests/"
            f"{self.service_request.id}/assign/",
            {},
            format="json"
        )

        print(
            "MISSING ASSIGNED_TO STATUS:",
            response.status_code
        )
        print(
            "MISSING ASSIGNED_TO DATA:",
            response.data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.data["detail"],
            "assigned_to is required."
        )

    def test_admin_can_assign_service_request(self):
        response = self.client.patch(
            f"/api/v1/service-requests/{self.service_request.id}/assign/",
            {
                "assigned_to": self.support_engineer.id
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            response.data["success"]
        )

        self.service_request.refresh_from_db()

        self.assertEqual(
            self.service_request.assigned_to_id,
            self.support_engineer.id
        )

    def test_support_engineer_cannot_assign_service_request(self):

        self.authenticate_user(
            self.support_engineer
        )

        response = self.client.patch(
            f"/api/v1/service-requests/"
            f"{self.service_request.id}/assign/",
            {
                "assigned_to": self.admin_user.id
            },
            format="json"
        )

        print(
            "SUPPORT ASSIGN STATUS:",
            response.status_code
        )

        print(
            "SUPPORT ASSIGN DATA:",
            response.data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertFalse(
            response.data["success"]
        )

        self.assertEqual(
            response.data["status_code"],
            403
        )

        self.assertEqual(
            response.data["message"],
            "You do not have permission to perform this action."
        )

        self.assertIn(
            "errors",
            response.data
        )

        self.assertIn(
            "detail",
            response.data["errors"]
        )
        
    def test_assign_without_assigned_to_returns_400(self):
        response = self.client.patch(
            f"/api/v1/service-requests/{self.service_request.id}/assign/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.data["detail"],
            "assigned_to is required."
        )