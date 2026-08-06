from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncMonth

from incidents.models import Incident   # Change if your app name is different


@login_required
def dashboard(request):

    # SLA Breaches by Month
    sla_data = (
        Incident.objects.filter(resolved_at__gt=F("sla_due"))
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    # Average Resolution Time
    resolution_data = (
        Incident.objects.filter(resolved_at__isnull=False)
        .annotate(
            month=TruncMonth("created_at"),
            resolution_time=ExpressionWrapper(
                F("resolved_at") - F("created_at"),
                output_field=DurationField(),
            ),
        )
        .values("month")
        .annotate(avg_resolution=Avg("resolution_time"))
        .order_by("month")
    )

    for row in resolution_data:
        if row["avg_resolution"]:
            row["avg_hours"] = round(
                row["avg_resolution"].total_seconds() / 3600,
                2,
            )
        else:
            row["avg_hours"] = 0

    context = {
        "sla_data": sla_data,
        "resolution_data": resolution_data,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )