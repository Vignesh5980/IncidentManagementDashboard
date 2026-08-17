from rest_framework import generics, status

from incidents.models import Incident
from .serializers import IncidentSerializer
from .permissions import IncidentAPIPermission
from rest_framework.permissions import BasePermission
from api.responses import success_response

class IncidentListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = IncidentSerializer

    permission_classes = [
        IncidentAPIPermission
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

    def delete(self, request, *args, **kwargs):
        incident = self.get_object()

        incident.is_deleted = True
        incident.save()

        return success_response(
            data=None,
            message="Incident deleted successfully.",
            status_code=status.HTTP_204_NO_CONTENT
        )