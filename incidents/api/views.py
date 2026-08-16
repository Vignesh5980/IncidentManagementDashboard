from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from incidents.models import Incident
from .serializers import IncidentSerializer


class IncidentListCreateAPIView(generics.ListCreateAPIView):

    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Incident.objects.filter(
            is_deleted=False
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )


class IncidentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Incident.objects.filter(
            is_deleted=False
        )