from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):

    ADMIN = 'ADMIN'
    TEAM_LEAD = 'TEAM_LEAD'
    SUPPORT = 'SUPPORT'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (TEAM_LEAD, 'Team Lead'),
        (SUPPORT, 'Support Engineer'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=SUPPORT
    )

    def __str__(self):
        return self.username