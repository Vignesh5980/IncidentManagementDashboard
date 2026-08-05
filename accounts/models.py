from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TEAM_LEAD = "TEAM_LEAD", "Team Lead"
        SUPPORT = "SUPPORT", "Support Engineer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SUPPORT,
    )

    def __str__(self):
        return self.username