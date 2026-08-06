from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Incident(models.Model):

    PRIORITY_CHOICES = [
        ('P1', 'P1 - Critical'),
        ('P2', 'P2 - High'),
        ('P3', 'P3 - Medium'),
        ('P4', 'P4 - Low'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('PENDING', 'Pending'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    incident_number = models.CharField(
        max_length=15,
        unique=True,
        editable=False
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    application = models.CharField(max_length=100)

    priority = models.CharField(
        max_length=2,
        choices=PRIORITY_CHOICES,
        default='P3'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_incidents'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    sla_due = models.DateTimeField(
        blank=True,
        null=True
    )

    resolved_at = models.DateTimeField(
        blank=True,
        null=True
    )

    root_cause = models.TextField(blank=True)

    resolution = models.TextField(blank=True)

    # Soft Delete
    is_deleted = models.BooleanField(default=False)

    class Meta:

        ordering = ['-created_at']

        indexes = [

            models.Index(fields=['priority']),

            models.Index(fields=['status']),

            models.Index(fields=['application']),

            models.Index(fields=['assigned_to']),

            models.Index(fields=['created_at']),

        ]

    def __str__(self):
        return self.incident_number

    def save(self, *args, **kwargs):

        # Generate Incident Number
        if not self.incident_number:

            last = Incident.objects.order_by('id').last()

            if last:
                number = last.id + 1
            else:
                number = 1

            self.incident_number = f"INC{number:06d}"

        # Calculate SLA
        if not self.sla_due:

            if self.priority == "P1":
                self.sla_due = timezone.now() + timedelta(hours=1)

            elif self.priority == "P2":
                self.sla_due = timezone.now() + timedelta(hours=4)

            elif self.priority == "P3":
                self.sla_due = timezone.now() + timedelta(hours=8)

            else:
                self.sla_due = timezone.now() + timedelta(hours=24)

        # Automatically set Resolved Time
        if self.status == "RESOLVED" and not self.resolved_at:
            self.resolved_at = timezone.now()

        super().save(*args, **kwargs)


class Comment(models.Model):

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.incident.incident_number}"


class IncidentHistory(models.Model):

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='history'
    )

    action = models.CharField(max_length=255)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.incident.incident_number} - {self.action}"