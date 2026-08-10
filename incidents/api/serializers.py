from rest_framework import serializers

from incidents.models import Incident


class IncidentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Incident

        fields = [
            "id",
            "incident_number",
            "title",
            "description",
            "priority",
            "status",
            "application",
            "assigned_to",
            "created_at",
            "resolved_at",
        ]

        read_only_fields = [
            "id",
            "incident_number",
            "created_at",
            "resolved_at",
        ]