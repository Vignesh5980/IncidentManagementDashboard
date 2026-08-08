from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from incidents.models import Incident
from problems.models import Problem
from changes.models import Change
from service_requests.models import ServiceRequest
from incidents.models import KnownError

@login_required
def dashboard(request):

    # =========================================================
    # INCIDENTS
    # =========================================================

    total_incidents = Incident.objects.count()

    open_incidents = Incident.objects.filter(
        status="OPEN"
    ).count()

    in_progress_incidents = Incident.objects.filter(
        status="IN_PROGRESS"
    ).count()

    resolved_incidents = Incident.objects.filter(
        status="RESOLVED"
    ).count()


    # =========================================================
    # SERVICE REQUESTS
    # =========================================================

    total_service_requests = ServiceRequest.objects.count()

    in_progress_service_requests = ServiceRequest.objects.filter(
        status=ServiceRequest.IN_PROGRESS
    ).count()

    closed_service_requests = ServiceRequest.objects.filter(
        status=ServiceRequest.CLOSED
    ).count()

    rejected_service_requests = ServiceRequest.objects.filter(
        status=ServiceRequest.REJECTED
    ).count()


    # =========================================================
    # PROBLEMS
    # =========================================================

    total_problems = Problem.objects.count()


    # =========================================================
    # CHANGES
    # =========================================================

    total_changes = Change.objects.count()


    # =========================================================
    # KEDB
    # =========================================================

    total_kedb = KnownError.objects.count()


    # =========================================================
    # RECENT INCIDENTS
    # =========================================================

    recent_incidents = (
        Incident.objects
        .order_by("-created_at")[:5]
    )


    # =========================================================
    # DASHBOARD
    # =========================================================

    context = {

        # Incidents
        "total_incidents": total_incidents,
        "open_incidents": open_incidents,
        "in_progress_incidents": in_progress_incidents,
        "resolved_incidents": resolved_incidents,

        # Service Requests
        "total_service_requests": total_service_requests,
        "in_progress_service_requests": in_progress_service_requests,
        "closed_service_requests": closed_service_requests,
        "rejected_service_requests": rejected_service_requests,

        # Problems
        "total_problems": total_problems,

        # Changes
        "total_changes": total_changes,

        # KEDB
        "total_kedb": total_kedb,

        # Recent incidents
        "recent_incidents": recent_incidents,
    }


    return render(
        request,
        "dashboard/dashboard.html",
        context
    )