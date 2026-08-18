from rest_framework import generics, status
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import BasePermission

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
)

from incidents.models import Incident
from .serializers import IncidentSerializer, IncidentResponseSerializer
from .permissions import IncidentAPIPermission
from api.responses import success_response

@extend_schema_view(
    get=extend_schema(
        summary="Retrieve incident",
        description="Retrieve a single active incident by ID.",
        responses={
            200: OpenApiResponse(
                response=IncidentResponseSerializer,
                description="Incident retrieved successfully.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
            404: OpenApiResponse(
                description="Incident not found.",
            ),
        },
    ),
    post=extend_schema(
        summary="Create incident",
        description=(
            "Create a new incident. "
            "The authenticated user is automatically set as the creator."
        ),
        responses={
            201: OpenApiResponse(
                response=IncidentResponseSerializer,
                description="Incident created successfully.",
            ),
            400: OpenApiResponse(
                description="Invalid incident data.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
            429: OpenApiResponse(
                description="Request rate limit exceeded.",
            ),
        },
    ),
    
)


class IncidentListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = IncidentSerializer
    pagination_class = None
    permission_classes = [
        IncidentAPIPermission
    ]

    throttle_classes = [
        UserRateThrottle
    ]

    def get_queryset(self):

        return Incident.objects.filter(
            is_deleted=False
        ).order_by(
            "-created_at"
        )

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()

        serializer = self.get_serializer(
            queryset,
            many=True
        )

        return success_response(
            data=serializer.data,
            message="Incidents retrieved successfully."
        )
    @extend_schema(
        summary="Create incident",
        description=(
            "Create a new incident. "
            "The authenticated user is automatically set as the creator."
        ),
        request=IncidentSerializer,
        responses={
            201: OpenApiResponse(
                response=IncidentSerializer,
                description="Incident created successfully.",
            ),
            400: OpenApiResponse(
                description="Invalid incident data.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
            429: OpenApiResponse(
                description="Request rate limit exceeded.",
            ),
        },
    )
    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save(
            created_by=request.user
        )

        return success_response(
            data=serializer.data,
            message="Incident created successfully.",
            status_code=status.HTTP_201_CREATED
        )


@extend_schema_view(
    put=extend_schema(
        summary="Update incident",
        description="Update an existing incident.",
        responses={
            200: OpenApiResponse(
                response=IncidentResponseSerializer,
                description="Incident updated successfully.",
            ),
            400: OpenApiResponse(
                description="Invalid incident data.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
            404: OpenApiResponse(
                description="Incident not found.",
            ),
        },
    ),
    patch=extend_schema(
        summary="Partially update incident",
        description="Partially update an existing incident.",
        responses={
            200: OpenApiResponse(
                response=IncidentResponseSerializer,
                description="Incident updated successfully.",
            ),
            400: OpenApiResponse(
                description="Invalid incident data.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
            404: OpenApiResponse(
                description="Incident not found.",
            ),
        },
    ),

    delete=extend_schema(
        summary="Delete incident",
        description=(
            "Soft delete an incident. "
            "The incident is marked as deleted and removed "
            "from normal API listings."
        ),
        responses={
            204: OpenApiResponse(
                description="Incident deleted successfully.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
            404: OpenApiResponse(
                description="Incident not found.",
            ),
        },
    ),
)
class IncidentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = IncidentSerializer

    permission_classes = [
        IncidentAPIPermission
    ]

    def get_queryset(self):

        return Incident.objects.filter(
            is_deleted=False
        )

    def get(self, request, *args, **kwargs):

        incident = self.get_object()

        serializer = self.get_serializer(
            incident
        )

        return success_response(
            data=serializer.data,
            message="Incident retrieved successfully."
        )

    def put(self, request, *args, **kwargs):

        incident = self.get_object()

        serializer = self.get_serializer(
            incident,
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return success_response(
            data=serializer.data,
            message="Incident updated successfully."
        )

    def patch(self, request, *args, **kwargs):

        incident = self.get_object()

        serializer = self.get_serializer(
            incident,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return success_response(
            data=serializer.data,
            message="Incident updated successfully."
        )
    @extend_schema(
        summary="List incidents",
        description=(
            "Retrieve all active incidents. "
            "Soft-deleted incidents are excluded."
        ),
            responses={
            200: OpenApiResponse(
                response=IncidentResponseSerializer,
                description="Incidents retrieved successfully.",
            ),

            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
            429: OpenApiResponse(
                description="Request rate limit exceeded.",
            ),
        },
    )
    def delete(self, request, *args, **kwargs):
        incident = self.get_object()

        incident.is_deleted = True
        incident.save()

        return success_response(
            data=None,
            message="Incident deleted successfully.",
            status_code=status.HTTP_204_NO_CONTENT
        )