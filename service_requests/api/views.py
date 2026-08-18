from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
)

from service_requests.models import ServiceRequest

from .serializers import ServiceRequestSerializer
from .permissions import ServiceRequestAPIPermission

@extend_schema_view(
    get=extend_schema(
        summary="List service requests",
        description=(
            "Retrieve service requests with optional filtering, "
            "searching, and ordering."
        ),
        responses={
            200: OpenApiResponse(
                response=ServiceRequestSerializer(many=True),
                description="Service requests retrieved successfully.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
        },
    ),

    post=extend_schema(
        summary="Create service request",
        description=(
            "Create a new service request. "
            "The authenticated user is automatically assigned "
            "as the requester."
        ),
        responses={
            201: OpenApiResponse(
                response=ServiceRequestSerializer,
                description="Service request created successfully.",
            ),
            400: OpenApiResponse(
                description="Invalid service request data.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
        },
    ),
)


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

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(
            self.get_queryset()
        )

        serializer = self.get_serializer(
            queryset,
            many=True
        )

        return Response({
            "success": True,
            "data": serializer.data,
        })

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        self.perform_create(serializer)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):

        serializer.save(
            requester=self.request.user
        )

@extend_schema_view(
    get=extend_schema(
        summary="Retrieve service request",
        description=(
            "Retrieve a single service request by ID."
        ),
        responses={
            200: OpenApiResponse(
                response=ServiceRequestSerializer,
                description="Service request retrieved successfully.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
            404: OpenApiResponse(
                description="Service request not found.",
            ),
        },
    ),

    put=extend_schema(
        summary="Update service request",
        description=(
            "Replace an existing service request."
        ),
        responses={
            200: OpenApiResponse(
                response=ServiceRequestSerializer,
                description="Service request updated successfully.",
            ),
            400: OpenApiResponse(
                description="Invalid service request data.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
            404: OpenApiResponse(
                description="Service request not found.",
            ),
        },
    ),

    patch=extend_schema(
        summary="Partially update service request",
        description=(
            "Partially update an existing service request."
        ),
        responses={
            200: OpenApiResponse(
                response=ServiceRequestSerializer,
                description="Service request updated successfully.",
            ),
            400: OpenApiResponse(
                description="Invalid service request data.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
            404: OpenApiResponse(
                description="Service request not found.",
            ),
        },
    ),

    delete=extend_schema(
        summary="Delete service request",
        description=(
            "Delete an existing service request."
        ),
        responses={
            204: OpenApiResponse(
                description="Service request deleted successfully.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Permission denied.",
            ),
            404: OpenApiResponse(
                description="Service request not found.",
            ),
        },
    ),
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

    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()

        serializer = self.get_serializer(
            instance
        )

        return Response({
            "success": True,
            "data": serializer.data,
        })

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop(
            "partial",
            False
        )

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True
        )

        self.perform_update(serializer)

        return Response({
            "success": True,
            "data": serializer.data,
        })

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        self.perform_destroy(instance)

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

@extend_schema_view(
    put=extend_schema(
        summary="Assign service request",
        description=(
            "Assign a service request to a user. "
            "Only Admin and Team Lead users are permitted "
            "to perform this operation."
        ),
        responses={
            200: OpenApiResponse(
                response=ServiceRequestSerializer,
                description="Service request assigned successfully.",
            ),
            400: OpenApiResponse(
                description="assigned_to is required.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Only Admin or Team Lead can assign requests.",
            ),
            404: OpenApiResponse(
                description="Service request not found.",
            ),
        },
    ),

    patch=extend_schema(
        summary="Partially assign service request",
        description=(
            "Assign a service request to a user. "
            "Only Admin and Team Lead users are permitted "
            "to perform this operation."
        ),
        responses={
            200: OpenApiResponse(
                response=ServiceRequestSerializer,
                description="Service request assigned successfully.",
            ),
            400: OpenApiResponse(
                description="assigned_to is required.",
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
            ),
            403: OpenApiResponse(
                description="Only Admin or Team Lead can assign requests.",
            ),
            404: OpenApiResponse(
                description="Service request not found.",
            ),
        },
    ),
)

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

        return Response({
            "success": True,
            "data": serializer.data,
        })