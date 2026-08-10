import csv
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.db.models.functions import TruncMonth

from django.shortcuts import get_object_or_404, redirect, render
from datetime import timedelta
from django.http import JsonResponse, request

from .forms import (
    ServiceRequestApprovalForm,
    ServiceRequestForm,
    ServiceRequestAttachmentForm,
    ServiceRequestCommentForm,
    ServiceRequestUpdateForm,
    ServiceCatalog,
)

from .models import (
    ServiceRequest,
    ServiceRequestApproval,
    ServiceRequestAttachment,
    ServiceRequestComment,
    ServiceRequestHistory,
    ServiceCatalog,
)


# ============================================================
# STATUS TRANSITION VALIDATION
# ============================================================

def is_valid_status_transition(current_status, new_status):

    allowed_transitions = {

        ServiceRequest.DRAFT: [
            ServiceRequest.SUBMITTED,
            ServiceRequest.CLOSED,
            ServiceRequest.REJECTED,
        ],

        ServiceRequest.SUBMITTED: [
            ServiceRequest.PENDING_APPROVAL,
            ServiceRequest.APPROVED,
            ServiceRequest.ASSIGNED,
            ServiceRequest.REJECTED,
        ],

        ServiceRequest.PENDING_APPROVAL: [
            ServiceRequest.APPROVED,
            ServiceRequest.REJECTED,
        ],

        ServiceRequest.APPROVED: [
            ServiceRequest.ASSIGNED,
            ServiceRequest.IN_PROGRESS,
        ],

        ServiceRequest.ASSIGNED: [
            ServiceRequest.IN_PROGRESS,
            ServiceRequest.FULFILLED,
        ],

        ServiceRequest.IN_PROGRESS: [
            ServiceRequest.ASSIGNED,
            ServiceRequest.FULFILLED,
            ServiceRequest.CLOSED,
        ],

        ServiceRequest.FULFILLED: [
            ServiceRequest.CLOSED,
            ServiceRequest.IN_PROGRESS,
        ],

        ServiceRequest.REJECTED: [],

        ServiceRequest.CLOSED: [],
    }

    # Allow saving without changing the status
    if current_status == new_status:
        return True

    return new_status in allowed_transitions.get(
        current_status,
        []
    )

breached_requests = (
    ServiceRequest.objects
    .filter(
        sla_due_at__lt=timezone.now()
    )
    .exclude(
        status__in=[
            ServiceRequest.CLOSED,
            ServiceRequest.FULFILLED,
            ServiceRequest.REJECTED,
        ]
    )
)

def is_sla_breached(service_request):

    if not service_request.sla_due_at:
        return False

    if service_request.status in [
        ServiceRequest.CLOSED,
        ServiceRequest.FULFILLED,
        ServiceRequest.REJECTED,
    ]:
        return False

    return timezone.now() > service_request.sla_due_at



def get_sla_remaining(service_request):

    if not service_request.sla_due_at:
        return None

    remaining = (
        service_request.sla_due_at
        - timezone.now()
    )

    return remaining

# ============================================================
# SERVICE REQUEST LIST
# ============================================================

@login_required
def service_request_list(request):

    requests = (
        ServiceRequest.objects
        .select_related(
            "service",
            "requester",
            "assigned_to",
        )
        .order_by("-created_at")
    )

    total_requests = requests.count()

    in_progress_requests = requests.filter(
        status=ServiceRequest.IN_PROGRESS
    ).count()

    closed_requests = requests.filter(
        status=ServiceRequest.CLOSED
    ).count()

    rejected_requests = requests.filter(
        status=ServiceRequest.REJECTED
    ).count()

    return render(
        request,
        "service_requests/service_request_list.html",
        {
            "requests": requests,
            "total_requests": total_requests,
            "in_progress_requests": in_progress_requests,
            "closed_requests": closed_requests,
            "rejected_requests": rejected_requests,
        }
    )


# ============================================================
# CREATE SERVICE REQUEST
# ============================================================

@login_required
def create_service_request(request):

    if request.method == "POST":

        form = ServiceRequestForm(
            request.POST
        )

        if form.is_valid():

            service_request = form.save(
                commit=False
            )

            # Automatically assign logged-in user
            # if requester is not supplied.
            if not service_request.requester_id:
                service_request.requester = request.user

            service_request.save()

            # ------------------------------------------------
            # Approval handling
            # ------------------------------------------------

            if (
                service_request.service
                and service_request.service.requires_approval
            ):

                old_status = service_request.status

                service_request.status = (
                    ServiceRequest.PENDING_APPROVAL
                )

                service_request.save(
                    update_fields=["status"]
                )

                ServiceRequestApproval.objects.create(
                    service_request=service_request,
                    status=ServiceRequestApproval.PENDING
                )

                create_request_history(
                    service_request,
                    request.user,
                    "Approval requested",
                    old_status,
                    service_request.status
                )

            else:

                # If approval is not required,
                # move submitted request to SUBMITTED.
                if service_request.status == ServiceRequest.DRAFT:

                    old_status = service_request.status

                    service_request.status = (
                        ServiceRequest.SUBMITTED
                    )

                    service_request.save(
                        update_fields=["status"]
                    )

                    create_request_history(
                        service_request,
                        request.user,
                        "Request submitted",
                        old_status,
                        service_request.status
                    )

            messages.success(
                request,
                (
                    f"Service Request "
                    f"{service_request.request_number} "
                    f"created successfully."
                )
            )

            return redirect(
                "service_request_detail",
                pk=service_request.pk
            )

    else:

        form = ServiceRequestForm(
            initial={
                "requester": request.user
            }
        )

    return render(
        request,
        "service_requests/service_request_create.html",
        {
            "form": form,
        }
    )


# ============================================================
# UPDATE SERVICE REQUEST
# ============================================================

@login_required
def update_service_request(request, pk):

    service_request = get_object_or_404(
        ServiceRequest,
        pk=pk
    )

    if request.method == "POST":

        form = ServiceRequestUpdateForm(
            request.POST,
            instance=service_request,
            user=request.user
        )

        if form.is_valid():

            old_status = service_request.status
            old_assigned_to = service_request.assigned_to

            service_request = form.save()

            # Create history for status change
            if old_status != service_request.status:

                ServiceRequestHistory.objects.create(
                    service_request=service_request,
                    changed_by=request.user,
                    action="Status Changed",
                    old_value=old_status,
                    new_value=service_request.status,
                )

            # Create history for assignment change
            if old_assigned_to != service_request.assigned_to:

                ServiceRequestHistory.objects.create(
                    service_request=service_request,
                    changed_by=request.user,
                    action="Assignment Changed",
                    old_value=(
                        str(old_assigned_to)
                        if old_assigned_to
                        else "Unassigned"
                    ),
                    new_value=(
                        str(service_request.assigned_to)
                        if service_request.assigned_to
                        else "Unassigned"
                    ),
                )

            messages.success(
                request,
                "Service request updated successfully."
            )

            return redirect(
                "service_request_detail",
                pk=service_request.pk
            )

    else:

        form = ServiceRequestUpdateForm(
            instance=service_request,
            user=request.user
        )

    return render(
        request,
        "service_requests/service_request_form.html",
        {
            "form": form,
            "service_request": service_request,
            "is_update": True,
        }
    )


# ============================================================
# SERVICE REQUEST DETAIL
# ============================================================

@login_required
def service_request_detail(request, pk):

    service_request = get_object_or_404(
        ServiceRequest,
        pk=pk
    )

    sla_breached = is_sla_breached(
        service_request
    )

    sla_remaining = get_sla_remaining(
        service_request
    )

    comment_form = (
        ServiceRequestCommentForm()
    )

    attachment_form = (
        ServiceRequestAttachmentForm()
    )

    return render(
        request,
        "service_requests/service_request_detail.html",
        {
            "service_request": service_request,
            "comment_form": comment_form,
            "attachment_form": attachment_form,
            "sla_breached": sla_breached,
            "sla_remaining": sla_remaining,
        }
    )


# ============================================================
# DELETE SERVICE REQUEST
# ============================================================

@login_required
def delete_service_request(request, pk):

    service_request = get_object_or_404(
        ServiceRequest,
        pk=pk
    )

    if request.method == "POST":

        request_number = (
            service_request.request_number
        )

        service_request.delete()

        messages.success(
            request,
            (
                f"Service Request "
                f"{request_number} "
                f"deleted successfully."
            )
        )

        return redirect(
            "service_request_list"
        )

    return render(
        request,
        "service_requests/service_request_confirm_delete.html",
        {
            "service_request": service_request,
        }
    )


# ============================================================
# ADD COMMENT
# ============================================================

@login_required
def add_service_request_comment(request, pk):

    service_request = get_object_or_404(
        ServiceRequest,
        pk=pk
    )

    if request.method == "POST":

        comment_text = request.POST.get(
            "comment",
            ""
        ).strip()

        if comment_text:

            ServiceRequestComment.objects.create(
                service_request=service_request,
                user=request.user,
                comment=comment_text
            )

            messages.success(
                request,
                "Comment added successfully."
            )

        else:

            messages.error(
                request,
                "Comment cannot be empty."
            )

    return redirect(
        "service_request_detail",
        pk=service_request.pk
    )


# ============================================================
# ADD ATTACHMENT
# ============================================================

@login_required
def add_service_request_attachment(request, pk):

    service_request = get_object_or_404(
        ServiceRequest,
        pk=pk
    )

    if request.method == "POST":

        uploaded_file = request.FILES.get(
            "file"
        )

        if uploaded_file:

            ServiceRequestAttachment.objects.create(
                service_request=service_request,
                file=uploaded_file,
                uploaded_by=request.user
            )

            messages.success(
                request,
                "Attachment uploaded successfully."
            )

        else:

            messages.error(
                request,
                "Please select a file to upload."
            )

    return redirect(
        "service_request_detail",
        pk=service_request.pk
    )


# ============================================================
# CREATE REQUEST HISTORY
# ============================================================

def create_request_history(
    service_request,
    user,
    action,
    old_value="",
    new_value=""
):

    ServiceRequestHistory.objects.create(
        service_request=service_request,
        changed_by=user,
        action=action,
        old_value=old_value,
        new_value=new_value,
    )


# ============================================================
# APPROVAL PERMISSION
# ============================================================

def can_approve_service_request(user):

    return getattr(
        user,
        "role",
        None
    ) in [
        "ADMIN",
        "TEAM_LEAD",
    ]


# ============================================================
# APPROVE SERVICE REQUEST
# ============================================================

@login_required
def approve_service_request(request, pk):

    service_request = get_object_or_404(
        ServiceRequest,
        pk=pk
    )

    # --------------------------------------------------------
    # Permission check
    # --------------------------------------------------------

    if not can_approve_service_request(
        request.user
    ):

        messages.error(
            request,
            "You do not have permission to approve requests."
        )

        return redirect(
            "service_request_detail",
            pk=pk
        )

    # --------------------------------------------------------
    # Status check
    # --------------------------------------------------------

    if service_request.status != (
        ServiceRequest.PENDING_APPROVAL
    ):

        messages.error(
            request,
            "This request is not awaiting approval."
        )

        return redirect(
            "service_request_detail",
            pk=pk
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        form = ServiceRequestApprovalForm(
            request.POST
        )

        if form.is_valid():

            decision = form.cleaned_data[
                "decision"
            ]

            comments = form.cleaned_data[
                "comments"
            ]

            # ------------------------------------------------
            # Get pending approval
            # ------------------------------------------------

            approval = (
                service_request.approvals
                .filter(
                    status=ServiceRequestApproval.PENDING
                )
                .first()
            )

            # ------------------------------------------------
            # Create approval if missing
            # ------------------------------------------------

            if not approval:

                approval = (
                    ServiceRequestApproval.objects.create(
                        service_request=service_request,
                        approver=request.user,
                        status=ServiceRequestApproval.PENDING,
                    )
                )

            # ------------------------------------------------
            # Update approval
            # ------------------------------------------------

            approval.approver = request.user
            approval.status = decision
            approval.comments = comments
            approval.approved_at = timezone.now()

            approval.save()

            # ------------------------------------------------
            # Update service request
            # ------------------------------------------------

            old_status = service_request.status

            if decision == ServiceRequestApproval.APPROVED:

                service_request.status = (
                    ServiceRequest.APPROVED
                )

                action = "Request approved"

            elif decision == ServiceRequestApproval.REJECTED:

                service_request.status = (
                    ServiceRequest.REJECTED
                )

                action = "Request rejected"

            else:

                messages.error(
                    request,
                    "Invalid approval decision."
                )

                return redirect(
                    "service_request_detail",
                    pk=pk
                )

            service_request.save(
                update_fields=["status"]
            )

            # ------------------------------------------------
            # History
            # ------------------------------------------------

            create_request_history(
                service_request,
                request.user,
                action,
                old_status,
                service_request.status
            )

            messages.success(
                request,
                (
                    f"{service_request.request_number} "
                    f"has been {decision.lower()}."
                )
            )

            return redirect(
                "service_request_detail",
                pk=pk
            )

    else:

        form = ServiceRequestApprovalForm()

    return render(
        request,
        "service_requests/service_request_approval.html",
        {
            "form": form,
            "service_request": service_request,
        }
    )

@login_required
def service_information(request, service_id):

    service = get_object_or_404(
        ServiceCatalog,
        pk=service_id,
        is_active=True,
    )

    return JsonResponse({
        "id": service.id,
        "name": service.name,
        "category": service.category,
        "subcategory": service.subcategory,
        "priority": service.default_priority,
        "sla_hours": service.sla_hours,
    })

@login_required
def create_service_request(request):

    if request.method == "POST":

        form = ServiceRequestForm(
            request.POST
        )

        if form.is_valid():

            service_request = form.save(
                commit=False
            )

            # Logged-in user becomes requester
            service_request.requester = request.user

            # ------------------------------------------------
            # Calculate SLA Due Date
            # ------------------------------------------------

            if service_request.service:

                sla_hours = (
                    service_request.service.sla_hours
                )

                service_request.sla_due_at = (
                    timezone.now()
                    + timedelta(hours=sla_hours)
                )

            service_request.save()

            messages.success(
                request,
                "Service request created successfully."
            )

            return redirect(
                "service_request_detail",
                pk=service_request.pk
            )

    else:

        form = ServiceRequestForm()

    return render(
        request,
        "service_requests/service_request_create.html",
        {
            "form": form,
        }
    )

@login_required
def service_request_dashboard(request):

    now = timezone.now()

    # -----------------------------
    # Summary Cards
    # -----------------------------

    total_requests = ServiceRequest.objects.count()

    open_requests = ServiceRequest.objects.filter(
        status__in=[
            "SUBMITTED",
            "ASSIGNED",
            "IN_PROGRESS",
        ]
    ).count()

    pending_approval = ServiceRequest.objects.filter(
        status="PENDING_APPROVAL"
    ).count()

    in_progress = ServiceRequest.objects.filter(
        status="IN_PROGRESS"
    ).count()

    sla_breached = ServiceRequest.objects.filter(
        sla_due_at__lt=now
    ).exclude(
        status__in=[
            "FULFILLED",
            "CLOSED",
            "REJECTED",
        ]
    ).count()

    sla_within = (
        ServiceRequest.objects
        .filter(
            sla_due_at__gte=now
        )
        .exclude(
            status__in=[
                "FULFILLED",
                "CLOSED",
                "REJECTED",
            ]
        )
        .count()
    )

    # -----------------------------
    # Monthly Trend
    # -----------------------------

    monthly_requests = (
        ServiceRequest.objects
        .annotate(
            month=TruncMonth("created_at")
        )
        .values("month")
        .annotate(
            total=Count("id")
        )
        .order_by("month")
    )

    monthly_labels = []

    monthly_values = []

    for item in monthly_requests:

        monthly_labels.append(
            item["month"].strftime("%b %Y")
        )

        monthly_values.append(
            item["total"]
        )

    # -----------------------------
    # Engineer Workload
    # -----------------------------

    engineer_workload = (
        ServiceRequest.objects
        .filter(
            assigned_to__isnull=False
        )
        .values(
            "assigned_to__username"
        )
        .annotate(
            total=Count("id")
        )
        .order_by("-total")
    )

    engineer_labels = []

    engineer_values = []

    for item in engineer_workload:

        engineer_labels.append(
            item["assigned_to__username"]
        )

        engineer_values.append(
            item["total"]
        )

    context = {

        "total_requests": total_requests,

        "open_requests": open_requests,

        "pending_approval": pending_approval,

        "in_progress": in_progress,

        "sla_breached": sla_breached,

        "sla_within": sla_within,

        "monthly_labels": monthly_labels,

        "monthly_values": monthly_values,

        "engineer_labels": engineer_labels,

        "engineer_values": engineer_values,
    }

    return render(
        request,
        "service_requests/service_request_dashboard.html",
        context
    )

@login_required
def service_request_list(request):

    requests = ServiceRequest.objects.all()

    search = request.GET.get(
        "search",
        ""
    ).strip()

    priority = request.GET.get(
        "priority",
        ""
    )

    status = request.GET.get(
        "status",
        ""
    )

    category = request.GET.get(
        "category",
        ""
    )

    if search:

        requests = requests.filter(
            Q(
                request_number__icontains=search
            )
            |
            Q(
                title__icontains=search
            )
            |
            Q(
                description__icontains=search
            )
        )

    if priority:

        requests = requests.filter(
            priority=priority
        )

    if status:

        requests = requests.filter(
            status=status
        )

    if category:

        requests = requests.filter(
            category_id=category
        )

    requests = requests.order_by(
        "-created_at"
    )

    categories = ServiceCatalog.objects.all()

    context = {

        "requests": requests,

        "categories": categories,

        "search": search,

        "selected_priority": priority,

        "selected_status": status,

        "selected_category": category,
    }

    return render(
        request,
        "service_requests/service_request_list.html",
        context
    )

@login_required
def export_service_requests_csv(request):

    if getattr(request.user, "role", None) not in [
        "ADMIN",
        "TEAM_LEAD",
    ]:

        messages.error(
            request,
            "You do not have permission to export requests."
        )

        return redirect(
            "service_request_list"
        )

    requests = ServiceRequest.objects.all()

    search = request.GET.get(
        "search",
        ""
    ).strip()

    priority = request.GET.get(
        "priority",
        ""
    )

    status = request.GET.get(
        "status",
        ""
    )

    category = request.GET.get(
        "category",
        ""
    )

    if search:

        requests = requests.filter(
            Q(
                request_number__icontains=search
            )
            |
            Q(
                title__icontains=search
            )
            |
            Q(
                description__icontains=search
            )
        )

    if priority:

        requests = requests.filter(
            priority=priority
        )

    if status:

        requests = requests.filter(
            status=status
        )

    if category:

        requests = requests.filter(
            category_id=category
        )

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        'attachment; filename="service_requests.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Request Number",
        "Title",
        "Priority",
        "Status",
        "Category",
        "Requester",
        "Assigned To",
        "Created At",
        "SLA Due",
    ])

    for item in requests:

        writer.writerow([
            item.request_number,
            item.title,
            item.priority,
            item.status,
            item.category,
            item.requester,
            item.assigned_to,
            item.created_at,
            item.sla_due_at,
        ])

    return response