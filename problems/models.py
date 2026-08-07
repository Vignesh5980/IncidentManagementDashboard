from django.db import models
from django.conf import settings

class Problem(models.Model):

    OPEN = "OPEN"
    RCA = "RCA"
    FIX_IN_PROGRESS = "FIX_IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

    STATUS_CHOICES = [
        (OPEN, "Open"),
        (RCA, "RCA In Progress"),
        (FIX_IN_PROGRESS, "Fix In Progress"),
        (RESOLVED, "Resolved"),
        (CLOSED, "Closed"),
    ]

    problem_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    title = models.CharField(max_length=250)
    description = models.TextField()
    application = models.CharField(max_length=100)
    root_cause = models.TextField(blank=True)
    workaround = models.TextField(blank=True)
    permanent_fix = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=OPEN
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_problems"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_problems"
    )
    incidents = models.ManyToManyField(
        "incidents.Incident",
        related_name="problems",
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.problem_number:
            last = Problem.objects.order_by("-id").first()

            if last:
                number = last.id + 1
            else:
                number = 1

            self.problem_number = f"PRB{number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.problem_number

class RCA(models.Model):

    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"

    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PENDING, "Pending Approval"),
        (APPROVED, "Approved"),
    ]

    problem = models.OneToOneField(
        Problem,
        on_delete=models.CASCADE,
        related_name="rca"
    )

    summary = models.TextField()

    root_cause = models.TextField()

    impact = models.TextField()

    corrective_action = models.TextField()

    preventive_action = models.TextField()

    # -----------------------------
    # 5 Whys Analysis
    # -----------------------------
    why1 = models.TextField(blank=True)

    why2 = models.TextField(blank=True)

    why3 = models.TextField(blank=True)

    why4 = models.TextField(blank=True)

    why5 = models.TextField(blank=True)

    # -----------------------------
    # Fishbone Analysis
    # -----------------------------
    people = models.TextField(blank=True)

    process = models.TextField(blank=True)

    technology = models.TextField(blank=True)

    environment = models.TextField(blank=True)

    measurement = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=DRAFT
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RCA - {self.problem.problem_number}"

class ProblemHistory(models.Model):

    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="history"
    )

    action = models.CharField(max_length=255)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        username = self.user.username if self.user else "System"
        return f"{self.problem.problem_number} - {self.action} ({username})"

class KnownError(models.Model):

    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (RETIRED, "Retired"),
    ]

    error_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    title = models.CharField(max_length=255)

    application = models.CharField(max_length=100)

    symptoms = models.TextField()

    workaround = models.TextField()

    permanent_fix = models.TextField()

    keywords = models.CharField(
        max_length=300,
        help_text="Comma separated keywords"
    )

    problem = models.OneToOneField(
        Problem,
        on_delete=models.CASCADE,
        related_name="known_error"
    )

    incidents = models.ManyToManyField(
        "incidents.Incident",
        related_name="known_errors",
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=ACTIVE
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.error_number:

            last = KnownError.objects.order_by("-id").first()

            number = last.id + 1 if last else 1

            self.error_number = f"KEDB{number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.error_number