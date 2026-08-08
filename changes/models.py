from django.db import models
from django.conf import settings


class Change(models.Model):

    STANDARD = "STANDARD"
    NORMAL = "NORMAL"
    EMERGENCY = "EMERGENCY"

    TYPE_CHOICES = [
        (STANDARD, "Standard"),
        (NORMAL, "Normal"),
        (EMERGENCY, "Emergency"),
    ]

    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    IMPLEMENTED = "IMPLEMENTED"
    FAILED = "FAILED"
    CLOSED = "CLOSED"

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PENDING, "Pending CAB"),
        (APPROVED, "Approved"),
        (SCHEDULED, "Scheduled"),
        (IMPLEMENTED, "Implemented"),
        (FAILED, "Failed"),
        (CLOSED, "Closed"),
    ]

    change_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    change_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=DRAFT,
    )

    application = models.CharField(max_length=100)

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="requested_changes",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_changes",
    )

    scheduled_start = models.DateTimeField(
        null=True, 
        blank=True
    )

    scheduled_end = models.DateTimeField(
        null=True, 
            blank=True
    )

    implementation_plan = models.TextField()

    rollback_plan = models.TextField()

    risk = models.TextField()

    impact = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        if not self.change_number:

            last = Change.objects.order_by("-id").first()

            if last:
                number = last.id + 1
            else:
                number = 1

            self.change_number = f"RFC{number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.change_number

class PIR(models.Model):

    change = models.OneToOneField(
        Change,
        on_delete=models.CASCADE,
        related_name="pir"
    )

    successful = models.BooleanField()

    observations = models.TextField()

    lessons = models.TextField()

    recommendations = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"PIR - {self.change.change_number}"