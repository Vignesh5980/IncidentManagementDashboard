import csv
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import IncidentCreateForm, CommentForm, IncidentUpdateForm
from .models import Incident, Comment, IncidentHistory, KnownError
from accounts.decorators import role_required
from accounts.models import CustomUser
from django.db.models import Q
from .utils import filter_incidents
from datetime import datetime
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

@login_required
def incident_list(request):

    incidents = filter_incidents(
        request,
        Incident.objects.select_related(
            "assigned_to",
            "created_by"
        )
    ).all()

    priority = request.GET.get('priority')
    status = request.GET.get('status')
    application = request.GET.get('application')
    engineer = request.GET.get('engineer')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    keyword = request.GET.get('keyword')

    if priority:
        incidents = incidents.filter(priority=priority)

    if status:
        incidents = incidents.filter(status=status)

    if application:
        incidents = incidents.filter(application=application)

    if engineer:
        incidents = incidents.filter(assigned_to_id=engineer)

    if start_date:
        incidents = incidents.filter(created_at__date__gte=start_date)

    if end_date:
        incidents = incidents.filter(created_at__date__lte=end_date)

    if keyword:
        incidents = incidents.filter(
            Q(incident_number__icontains=keyword) |
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword)
        )

    context = {

        "incidents": incidents,

        "engineers": CustomUser.objects.filter(
            role=CustomUser.SUPPORT
        ),

        "applications": Incident.objects.values_list(
            "application",
            flat=True
        ).distinct(),

        "selected_priority": priority,
        "selected_status": status,
        "selected_application": application,
        "selected_engineer": engineer,
        "keyword": keyword,
        "start_date": start_date,
        "end_date": end_date,

    }

    return render(
        request,
        "incidents/incident_list.html",
        context
    )

@login_required
def create_incident(request):

    if request.method == "POST":

        form = IncidentCreateForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():

            incident = form.save(commit=False)
            incident.created_by = request.user
            incident.save()

            messages.success(
                request,
                f"{incident.incident_number} created successfully."
            )

            return redirect('incident_list')

    else:

        form = IncidentCreateForm(user=request.user)

    return render(
        request,
        'incidents/incident_create.html',
        {
            'form': form
        }
    )


@login_required
def incident_detail(request, pk):

    incident = get_object_or_404(
        Incident,
        pk=pk,
        is_deleted=False
    )

    comments = incident.comments.all()
    history = incident.history.all()

    form = CommentForm()

    if request.method == "POST":

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)
            comment.incident = incident
            comment.user = request.user
            comment.save()

            IncidentHistory.objects.create(
                incident=incident,
                user=request.user,
                action="Added Comment"
            )

            messages.success(
                request,
                "Comment Added Successfully"
            )

            return redirect(
                'incident_detail',
                pk=pk
            )

    return render(
        request,
        'incidents/incident_detail.html',
        {
            'incident': incident,
            'comments': comments,
            'history': history,
            'form': form
        }
    )


@login_required
def update_incident(request, pk):

    incident = get_object_or_404(
        Incident,
        pk=pk,
        is_deleted=False
    )

    old_status = incident.status
    old_assignee = incident.assigned_to

    if request.method == "POST":

        form = IncidentUpdateForm(
            request.POST,
            instance=incident,
            user=request.user
        )

        if form.is_valid():

            incident = form.save()

            if old_status != incident.status:

                IncidentHistory.objects.create(
                    incident=incident,
                    user=request.user,
                    action=f"Status changed to {incident.get_status_display()}"
                )

            if old_assignee != incident.assigned_to:

                IncidentHistory.objects.create(
                    incident=incident,
                    user=request.user,
                    action=f"Assigned to {incident.assigned_to}"
                )

            messages.success(
                request,
                "Incident Updated Successfully"
            )

            return redirect(
                'incident_detail',
                pk=pk
            )

    else:

        form = IncidentUpdateForm(
            instance=incident,
            user=request.user
        )

    return render(
        request,
        'incidents/incident_update.html',
        {
            'form': form,
            'incident': incident
        }
    )


@login_required
@role_required([CustomUser.ADMIN])
def delete_incident(request, pk):

    incident = get_object_or_404(
        Incident,
        pk=pk,
        is_deleted=False
    )

    if request.method == "POST":

        IncidentHistory.objects.create(
            incident=incident,
            user=request.user,
            action=f"Deleted Incident {incident.incident_number}"
        )

        # Soft Delete
        incident.is_deleted = True
        incident.save()

        messages.success(
            request,
            "Incident deleted successfully."
        )

        return redirect("incident_list")

    return render(
        request,
        "incidents/incident_confirm_delete.html",
        {
            "incident": incident
        }
    )

@login_required
@role_required([CustomUser.ADMIN, CustomUser.TEAM_LEAD])
def export_incidents_csv(request):

    incidents = filter_incidents(
        request,
        Incident.objects.select_related(
            "assigned_to",
            "created_by"
        )
    )

    response = HttpResponse(content_type="text/csv")

    filename = datetime.now().strftime(
    "Incidents_%Y%m%d_%H%M.csv"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    response["Content-Disposition"] = (
        'attachment; filename="incidents.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Incident Number",
        "Title",
        "Application",
        "Priority",
        "Status",
        "Assigned To",
        "Created By",
        "Created At",
        "SLA Due",
        "Resolved At"
    ])

    for incident in incidents:

        writer.writerow([
            incident.incident_number,
            incident.title,
            incident.application,
            incident.priority,
            incident.get_status_display(),
            incident.assigned_to.username if incident.assigned_to else "",
            incident.created_by.username,
            incident.created_at.strftime("%d-%m-%Y %H:%M"),
            incident.sla_due.strftime("%d-%m-%Y %H:%M") if incident.sla_due else "",
            incident.resolved_at.strftime("%d-%m-%Y %H:%M") if incident.resolved_at else "",
        ])

    return response

@login_required
def dashboard(request):

    incidents = Incident.objects.select_related(
        "assigned_to"
    )

    open_count = incidents.filter(
        status="OPEN"
    ).count()

    resolved_count = incidents.filter(
        status="RESOLVED"
    ).count()

    p1_count = incidents.filter(
        priority="P1"
    ).count()

    sla_breached = incidents.filter(
        status__in=["OPEN", "ASSIGNED", "IN_PROGRESS"],
        sla_due__lt=timezone.now()
    ).count()

    avg_resolution = incidents.filter(
        resolved_at__isnull=False
    ).annotate(
        resolution_time=ExpressionWrapper(
            F("resolved_at") - F("created_at"),
            output_field=DurationField()
        )
    ).aggregate(
        avg=Avg("resolution_time")
    )["avg"]

    monthly_data = (
        incidents.annotate(
            month=TruncMonth("created_at")
        )
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    priority_data = (
        incidents.values("priority")
        .annotate(total=Count("id"))
        .order_by("priority")
    )

    engineer_data = (
        incidents.values("assigned_to__username")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    latest_incidents = incidents.order_by(
        "-created_at"
    )[:10]

    context = {

        "open_count": open_count,
        "resolved_count": resolved_count,
        "p1_count": p1_count,
        "sla_breached": sla_breached,
        "avg_resolution": avg_resolution,
        "monthly_data": monthly_data,
        "priority_data": priority_data,
        "engineer_data": engineer_data,
        "latest_incidents": latest_incidents,

    }

    return render(
        request,
        "incidents/dashboard.html",
        context
    )

@login_required
def kedb_list(request):

    known_errors = KnownError.objects.all().order_by("-created_at")

    open_count = known_errors.filter(
        status="Open"
    ).count()

    known_error_count = known_errors.filter(
        status="Known Error"
    ).count()

    resolved_count = known_errors.filter(
        status="Resolved"
    ).count()

    return render(
        request,
        "incidents/kedb_list.html",
        {
            "known_errors": known_errors,
            "open_count": open_count,
            "known_error_count": known_error_count,
            "resolved_count": resolved_count,
        }
    )


@login_required
def kedb_create(request):

    if request.method == "POST":

        title = request.POST.get("title")
        description = request.POST.get("description")
        root_cause = request.POST.get("root_cause")
        workaround = request.POST.get("workaround")
        solution = request.POST.get("solution")
        application = request.POST.get("application")
        status = request.POST.get("status")

        KnownError.objects.create(
            title=title,
            description=description,
            root_cause=root_cause,
            workaround=workaround,
            solution=solution,
            application=application,
            status=status,
            created_by=request.user
        )

        messages.success(
            request,
            "Known Error created successfully."
        )

        return redirect("kedb_list")

    return render(
        request,
        "incidents/kedb_create.html"
    )