from rest_framework import generics

from incidents.models import Incident

from .serializers import IncidentSerializer


class IncidentListCreateAPIView(
    generics.ListCreateAPIView
):

    queryset = Incident.objects.all().order_by("-created_at")

    serializer_class = IncidentSerializer


class IncidentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Incident.objects.all()

    serializer_class = IncidentSerializer
