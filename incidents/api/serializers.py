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

    # -------------------------
    # Field validation
    # -------------------------

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


    # -------------------------
    # Cross-field validation
    # -------------------------

    def validate(self, attrs):

        request = self.context.get("request")

        instance = self.instance

        # Use existing values during PATCH
        status = attrs.get(
            "status",
            getattr(instance, "status", None)
        )

        assigned_to = attrs.get(
            "assigned_to",
            getattr(instance, "assigned_to", None)
        )

        # --------------------------------
        # Rule 1:
        # Cannot move to IN_PROGRESS
        # without assigning an engineer
        # --------------------------------

        if status == "IN_PROGRESS" and not assigned_to:

            raise serializers.ValidationError(
                {
                    "assigned_to":
                    "An incident must be assigned before "
                    "moving to IN_PROGRESS."
                }
            )

        # --------------------------------
        # Rule 2:
        # Cannot resolve an unassigned incident
        # --------------------------------

        if status == "RESOLVED" and not assigned_to:

            raise serializers.ValidationError(
                {
                    "assigned_to":
                    "An incident must be assigned before "
                    "being resolved."
                }
            )

        # --------------------------------
        # Status transition validation
        # --------------------------------

        if instance:

            old_status = instance.status
            new_status = attrs.get(
                "status",
                old_status
            )

            allowed_transitions = {

                "OPEN": [
                    "OPEN",
                    "IN_PROGRESS",
                    "CLOSED",
                ],

                "IN_PROGRESS": [
                    "IN_PROGRESS",
                    "RESOLVED",
                    "CLOSED",
                ],

                "RESOLVED": [
                    "RESOLVED",
                    "CLOSED",
                ],

                "CLOSED": [
                    "CLOSED",
                ],
            }

            if (
                new_status != old_status
                and new_status not in allowed_transitions.get(
                    old_status,
                    []
                )
            ):

                raise serializers.ValidationError(
                    {
                        "status":
                        f"Cannot change status from "
                        f"{old_status} to {new_status}."
                    }
                )

        # --------------------------------
        # Role-aware validation
        # --------------------------------

        if request and request.user.is_authenticated:

            role = getattr(
                request.user,
                "role",
                None
            )

            # Support Engineer cannot reassign
            # an incident to another user
            if (
                role == "SUPPORT_ENGINEER"
                and "assigned_to" in attrs
            ):

                if (
                    instance
                    and instance.assigned_to_id
                    != attrs["assigned_to"].id
                ):

                    raise serializers.ValidationError(
                        {
                            "assigned_to":
                            "Support Engineers cannot "
                            "reassign incidents."
                        }
                    )

        return attrs