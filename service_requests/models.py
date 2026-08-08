from django.db import models
from django.conf import settings

class ServiceCatalog(models.Model):

    name = models.CharField(
        max_length=150
    )

    category = models.CharField(
        max_length=100
    )

    subcategory = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    default_priority = models.CharField(
        max_length=2,
        choices=[
            ("P1", "P1 - Critical"),
            ("P2", "P2 - High"),
            ("P3", "P3 - Medium"),
            ("P4", "P4 - Low"),
        ],
        default="P3"
    )

    sla_hours = models.PositiveIntegerField(
        default=24
    )

    requires_approval = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name

class ServiceRequest(models.Model):
    service = models.ForeignKey(
        ServiceCatalog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests"
    )
    # -----------------------------
    # Priority
    # -----------------------------
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (IN_PROGRESS, "In Progress"),
        (CLOSED, "Closed"),
        (REJECTED, "Rejected"),
    ]
    
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"

    PRIORITY_CHOICES = [
        (P1, "P1 - Critical"),
        (P2, "P2 - High"),
        (P3, "P3 - Medium"),
        (P4, "P4 - Low"),
    ]

    # -----------------------------
    # Status
    # -----------------------------

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    FULFILLED = "FULFILLED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (SUBMITTED, "Submitted"),
        (PENDING_APPROVAL, "Pending Approval"),
        (APPROVED, "Approved"),
        (ASSIGNED, "Assigned"),
        (IN_PROGRESS, "In Progress"),
        (FULFILLED, "Fulfilled"),
        (CLOSED, "Closed"),
        (REJECTED, "Rejected"),
    ]

    # -----------------------------
    # Request Number
    # -----------------------------

    request_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    # -----------------------------
    # Request Information
    # -----------------------------

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    category = models.CharField(
        max_length=100
    )

    subcategory = models.CharField(
        max_length=100
    )

    # -----------------------------
    # Users
    # -----------------------------

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_requests"
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_service_requests"
    )

    # -----------------------------
    # Priority / Status
    # -----------------------------

    priority = models.CharField(
        max_length=2,
        choices=PRIORITY_CHOICES,
        default=P3
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=DRAFT
    )

    # -----------------------------
    # SLA
    # -----------------------------

    sla_due_at = models.DateTimeField(
        null=True,
        blank=True
    )

    sla_breached = models.BooleanField(
        default=False
    )

    # -----------------------------
    # Timestamps
    # -----------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # -----------------------------
    # Generate REQ Number
    # -----------------------------

    def save(self, *args, **kwargs):

        if not self.request_number:

            last_request = (
                ServiceRequest.objects
                .order_by("-id")
                .first()
            )

            if last_request:
                number = last_request.id + 1
            else:
                number = 1

            self.request_number = (
                f"REQ{number:06d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.request_number

class ServiceRequestComment(models.Model):

    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.service_request.request_number} "
            f"- {self.user}"
        )

class ServiceRequestAttachment(models.Model):

    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="attachments"
    )

    file = models.FileField(
        upload_to="service_requests/"
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.file.name
    
class ServiceRequestApproval(models.Model):

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    ]

    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="approvals"
    )

    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    comments = models.TextField(
        blank=True
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )