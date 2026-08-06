from django.contrib import admin
from .models import Incident, Comment

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        'incident_number',
        'title',
        'priority',
        'status',
        'assigned_to',
        'created_at'
    )

    search_fields = (
        'incident_number',
        'title',
        'application'
    )

    list_filter = (
        'priority',
        'status',
        'application'
    )

admin.site.register(Comment)