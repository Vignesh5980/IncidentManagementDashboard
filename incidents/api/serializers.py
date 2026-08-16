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

    def validate_title(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Incident title cannot be empty."
            )

        if len(value) < 5:
            raise serializers.ValidationError(
                "Incident title must contain at least 5 characters."
            )

        return value

    def validate_description(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Incident description cannot be empty."
            )

        return value

    def validate_priority(self, value):

        allowed_priorities = [
            "P1",
            "P2",
            "P3",
            "P4",
        ]

        if value not in allowed_priorities:
            raise serializers.ValidationError(
                "Invalid priority."
            )

        return value