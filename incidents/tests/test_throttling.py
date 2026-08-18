from copy import deepcopy

from django.conf import settings
from django.core.cache import cache
from django.test import override_settings

from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.throttling import UserRateThrottle

from incidents.api.views import IncidentListCreateAPIView

from .base import BaseAPITestCase


# =========================================================
# Debug throttle
# =========================================================

class DebugUserRateThrottle(UserRateThrottle):

    scope = "user"

    def get_rate(self):
        return "2/minute"

    def allow_request(self, request, view):

        result = super().allow_request(
            request,
            view
        )

        print("\nTHROTTLE DEBUG:")

        print(
            "User:",
            str(request.user)
        )

        print(
            "Authenticated:",
            request.user.is_authenticated
        )

        print(
            "Scope:",
            self.scope
        )

        print(
            "Rate:",
            self.rate
        )

        print(
            "Num requests:",
            self.num_requests
        )

        print(
            "Duration:",
            self.duration
        )

        print(
            "Cache key:",
            getattr(
                self,
                "key",
                None
            )
        )

        print(
            "History:",
            list(
                getattr(
                    self,
                    "history",
                    []
                )
            )
        )

        print(
            "Allowed:",
            result
        )

        return result

# =========================================================
# Test-specific DRF settings
# =========================================================

test_rest_framework_settings = deepcopy(
    settings.REST_FRAMEWORK
)

test_rest_framework_settings.update(
    {
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.UserRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {
            **settings.REST_FRAMEWORK.get(
                "DEFAULT_THROTTLE_RATES",
                {}
            ),
            "user": "2/minute",
        },
    }
)


# =========================================================
# Throttling tests
# =========================================================

@override_settings(
    REST_FRAMEWORK=test_rest_framework_settings
)
class IncidentThrottleTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()

        api_settings.reload()

        cache.clear()

        self.authenticate_user(
            self.admin_user
        )

        self.original_throttle_classes = (
            IncidentListCreateAPIView.throttle_classes
        )

        IncidentListCreateAPIView.throttle_classes = [
            DebugUserRateThrottle
        ]

    def tearDown(self):

        # -------------------------------------------------
        # Restore original throttle configuration
        # -------------------------------------------------

        IncidentListCreateAPIView.throttle_classes = (
            self.original_throttle_classes
        )

        # -------------------------------------------------
        # Clear cache after test
        # -------------------------------------------------

        cache.clear()

        super().tearDown()

    def test_rate_limit_returns_429(self):

        # -------------------------------------------------
        # Debug DRF configuration
        # -------------------------------------------------

        print("\n" + "=" * 60)
        print("THROTTLING TEST")
        print("=" * 60)

        print(
            "\nTHROTTLE CLASSES:",
            api_settings.DEFAULT_THROTTLE_CLASSES
        )

        print(
            "\nTHROTTLE RATES:",
            api_settings.DEFAULT_THROTTLE_RATES
        )

        view = IncidentListCreateAPIView()

        print(
            "\nVIEW THROTTLES:",
            view.get_throttles()
        )

        # -------------------------------------------------
        # API endpoint
        # -------------------------------------------------

        url = "/api/v1/incidents/"

        # -------------------------------------------------
        # Request 1
        # -------------------------------------------------

        print("\n" + "-" * 60)
        print("REQUEST 1")
        print("-" * 60)

        response_1 = self.client.get(
            url
        )

        print(
            "Response:",
            response_1.status_code,
            response_1.data
        )

        # -------------------------------------------------
        # Request 2
        # -------------------------------------------------

        print("\n" + "-" * 60)
        print("REQUEST 2")
        print("-" * 60)

        response_2 = self.client.get(
            url
        )

        print(
            "Response:",
            response_2.status_code,
            response_2.data
        )

        # -------------------------------------------------
        # Request 3
        # -------------------------------------------------

        print("\n" + "-" * 60)
        print("REQUEST 3")
        print("-" * 60)

        response_3 = self.client.get(
            url
        )

        print(
            "Response:",
            response_3.status_code,
            response_3.data
        )

        # -------------------------------------------------
        # Assertions
        # -------------------------------------------------

        # Request 1 should succeed
        self.assertEqual(
            response_1.status_code,
            status.HTTP_200_OK
        )

        # Request 2 should succeed
        self.assertEqual(
            response_2.status_code,
            status.HTTP_200_OK
        )

        # Request 3 should be throttled
        self.assertEqual(
            response_3.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS
        )

        # -------------------------------------------------
        # Validate response structure
        # -------------------------------------------------

        print(
            "\n429 RESPONSE:",
            response_3.data
        )

        # Only check custom structure if your exception
        # handler formats throttling responses this way.
        if "success" in response_3.data:

            self.assertFalse(
                response_3.data["success"]
            )

        if "status_code" in response_3.data:

            self.assertEqual(
                response_3.data["status_code"],
                429
            )

        # DRF may return either "detail" or your custom
        # "message" field.
        self.assertTrue(
            "message" in response_3.data
            or
            "detail" in response_3.data
        )