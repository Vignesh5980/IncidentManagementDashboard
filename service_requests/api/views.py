from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)

from service_requests.models import ServiceRequest

from .serializers import ServiceRequestSerializer
from .permissions import ServiceRequestAPIPermission


class ServiceRequestListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = ServiceRequestSerializer

    permission_classes = [
        ServiceRequestAPIPermission
    ]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "priority",
        "status",
        "assigned_to",
        "service",
        "category",
    ]

    search_fields = [
        "request_number",
        "title",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "priority",
        "status",
        "sla_due_at",
    ]

    ordering = [
        "-created_at"
    ]

    def get_queryset(self):

        return (
            ServiceRequest.objects
            .select_related(
                "requester",
                "assigned_to",
                "service",
            )
            .all()
        )

    def perform_create(self, serializer):

        serializer.save(
            requester=self.request.user
        )

class ServiceRequestDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = (
        ServiceRequest.objects
        .select_related(
            "requester",
            "assigned_to",
            "service",
        )
        .all()
    )

    serializer_class = ServiceRequestSerializer

    permission_classes = [
        ServiceRequestAPIPermission
    ]

class ServiceRequestAssignAPIView(
    generics.UpdateAPIView
):

    queryset = ServiceRequest.objects.all()

    serializer_class = ServiceRequestSerializer

    permission_classes = [
        ServiceRequestAPIPermission
    ]

    def patch(
        self,
        request,
        *args,
        **kwargs
    ):

        service_request = self.get_object()

        role = getattr(
            request.user,
            "role",
            None
        )

        if role not in [
            "ADMIN",
            "TEAM_LEAD",
        ]:

            return Response(
                {
                    "detail":
                    "You do not have permission to assign requests."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        assigned_to = request.data.get(
            "assigned_to"
        )

        if not assigned_to:

            return Response(
                {
                    "detail":
                    "assigned_to is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        service_request.assigned_to_id = assigned_to

        service_request.save()

        serializer = self.get_serializer(
            service_request
        )

        return Response(
            serializer.data
        )