from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import ServiceRequest, ServiceRequestComment, ServiceRequestAttachment
from .forms import ServiceRequestForm

# ============================================================

# STATUS TRANSITION VALIDATION

# ============================================================

def is_valid_status_transition(current_status, new_status):

    allowed_transitions = {

        ServiceRequest.NEW: [
            ServiceRequest.IN_PROGRESS,
            ServiceRequest.CANCELLED,
        ],

        ServiceRequest.IN_PROGRESS: [
            ServiceRequest.ASSIGNED,
            ServiceRequest.PENDING,
            ServiceRequest.CANCELLED,
        ],

        ServiceRequest.ASSIGNED: [
            ServiceRequest.IN_PROGRESS,
            ServiceRequest.PENDING,
            ServiceRequest.RESOLVED,
            ServiceRequest.CANCELLED,
        ],

        ServiceRequest.PENDING: [
            ServiceRequest.IN_PROGRESS,
            ServiceRequest.ASSIGNED,
            ServiceRequest.CANCELLED,
        ],

        ServiceRequest.RESOLVED: [
            ServiceRequest.CLOSED,
            ServiceRequest.IN_PROGRESS,
        ],

        ServiceRequest.CLOSED: [],

        ServiceRequest.CANCELLED: [],

    }

    return new_status in allowed_transitions.get(
        current_status,
        []
    )

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

            # Automatically use logged-in user
            # if requester is not supplied.

            if not service_request.requester_id:

                service_request.requester = request.user

            service_request.save()

            messages.success(
                request,
                (
                    f"Service Request "
                    f"{service_request.request_number} "
                    f"created successfully."
                )
            )

            return redirect(
                "service_request_list"
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

        form = ServiceRequestForm(
            request.POST,
            instance=service_request
        )


    if form.is_valid():

        # ------------------------------------------------
        # Get current and new status
        # ------------------------------------------------

        current_status = service_request.status

        new_status = form.cleaned_data.get(
            "status"
        )


        # ------------------------------------------------
        # Validate status transition
        # ------------------------------------------------

        if not is_valid_status_transition(
            current_status,
            new_status
        ):

            form.add_error(
                "status",
                (
                    f"Invalid transition: "
                    f"{current_status} → {new_status}"
                )
            )

            return render(
                request,
                "service_requests/service_request_update.html",
                {
                    "form": form,
                    "service_request": service_request,
                }
            )


        # ------------------------------------------------
        # ASSIGNED requires engineer
        # ------------------------------------------------

        if (
            new_status == ServiceRequest.ASSIGNED
            and not form.cleaned_data.get(
                "assigned_to"
            )
        ):

            form.add_error(
                "assigned_to",
                "Please assign an engineer."
            )

            return render(
                request,
                "service_requests/service_request_update.html",
                {
                    "form": form,
                    "service_request": service_request,
                }
            )


        # ------------------------------------------------
        # RESOLVED requires assigned engineer
        # ------------------------------------------------

        if (
            new_status == ServiceRequest.RESOLVED
            and not form.cleaned_data.get(
                "assigned_to"
            )
        ):

            form.add_error(
                "assigned_to",
                "Please assign an engineer before resolving."
            )

            return render(
                request,
                "service_requests/service_request_update.html",
                {
                    "form": form,
                    "service_request": service_request,
                }
            )


        # ------------------------------------------------
        # Save changes
        # ------------------------------------------------

        service_request = form.save()


        messages.success(
            request,
            (
                f"Service Request "
                f"{service_request.request_number} "
                f"updated successfully."
            )
        )


        return redirect(
            "service_request_list"
        )


    else:

        form = ServiceRequestForm(
            instance=service_request
        )


    return render(
        request,
        "service_requests/service_request_update.html",
        {
            "form": form,
            "service_request": service_request,
        }
    )

# ============================================================

# SERVICE REQUEST DETAIL

# ============================================================

@login_required
def service_request_detail(request, pk):

    service_request = get_object_or_404(
        ServiceRequest.objects.select_related(
            "service",
            "requester",
            "assigned_to",
        ),
        pk=pk
    )


    return render(
        request,
        "service_requests/service_request_detail.html",
        {
            "service_request": service_request,
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

        return redirect(
            "service_request_detail",
            pk=service_request.pk
        )

    return redirect(
        "service_request_detail",
        pk=service_request.pk
    )

@login_required
def add_service_request_attachment(request, pk):

    service_request = get_object_or_404(
        ServiceRequest,
        pk=pk
    )

    if request.method == "POST":

        uploaded_file = request.FILES.get("file")

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