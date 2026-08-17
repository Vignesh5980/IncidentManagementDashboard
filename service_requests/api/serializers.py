from rest_framework import serializers
from django.utils import timezone
from service_requests.models import ServiceRequest
from service_requests.models import (
    ServiceRequest,
    ServiceRequestApproval,
)

class ServiceRequestSerializer(serializers.ModelSerializer):
    sla_status = serializers.SerializerMethodField()
    approval_status = serializers.SerializerMethodField()
    requester_name = serializers.CharField(
        source="requester.username",
        read_only=True
    )

    assigned_to_name = serializers.CharField(
        source="assigned_to.username",
        read_only=True
    )

    def get_sla_status(self, obj) -> str:

        if not obj.sla_due_at:
            return "NOT_CONFIGURED"

        completed_statuses = [
            "FULFILLED",
            "CLOSED",
            "REJECTED",
        ]

        if obj.status in completed_statuses:
            return "COMPLETED"

        if timezone.now() > obj.sla_due_at:
            return "BREACHED"

        return "WITHIN_SLA"

    class Meta:

        model = ServiceRequest

        fields = [
            "id",
            "request_number",
            "title",
            "description",
            "service",
            "category",
            "subcategory",
            "priority",
            "status",
            "requester",
            "requester_name",
            "assigned_to",
            "assigned_to_name",
            "created_at",
            "updated_at",
            "sla_due_at",
            "sla_status",
            "approval_status",
        ]

        read_only_fields = [
            "id",
            "request_number",
            "requester",
            "requester_name",
            "assigned_to_name",
            "created_at",
            "updated_at",
            "sla_due_at",
        ]

    def validate_title(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Service request title cannot be empty."
            )

        if len(value) < 5:
            raise serializers.ValidationError(
                "Title must contain at least 5 characters."
            )

        return value

    def validate_description(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Description cannot be empty."
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

    def get_approval_status(self, obj) -> str:

        approval = (
            ServiceRequestApproval.objects
            .filter(
                service_request=obj
            )
            .order_by("-created_at")
            .first()
        )

        if not approval:
            return "NOT_REQUIRED"

        return approval.status

    def validate_assigned_to(
        self,
        value
    ):

        request = self.context.get("request")

        if not request:
            return value

        role = getattr(
            request.user,
            "role",
            None
        )

        if role not in [
            "ADMIN",
            "TEAM_LEAD",
        ]:

            raise serializers.ValidationError(
                "Only Admin or Team Lead can assign requests."
            )

        return value