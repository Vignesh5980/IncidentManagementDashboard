from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ChangeForm, PIRForm
from .models import Change, PIR

@login_required
def change_list(request):

    changes = Change.objects.all().order_by("-created_at")

    # Search
    search = request.GET.get("search", "").strip()

    if search:
        changes = changes.filter(
            Q(change_number__icontains=search) |
            Q(title__icontains=search) |
            Q(application__icontains=search) |
            Q(description__icontains=search)
        )

    # Status filter
    status = request.GET.get("status", "").strip()

    if status:
        changes = changes.filter(status=status)

    # Change type filter
    change_type = request.GET.get("change_type", "").strip()

    if change_type:
        changes = changes.filter(change_type=change_type)

    # Dashboard counts
    context = {
        "changes": changes,

        # Total
        "total_changes": Change.objects.count(),

        # Status counts
        "pending_cab": Change.objects.filter(
            status=Change.PENDING
        ).count(),

        "approved_changes": Change.objects.filter(
            status=Change.APPROVED
        ).count(),

        "scheduled_changes": Change.objects.filter(
            status=Change.SCHEDULED
        ).count(),

        # Change Type counts
        "standard_changes": Change.objects.filter(
            change_type=Change.STANDARD
        ).count(),

        "normal_changes": Change.objects.filter(
            change_type=Change.NORMAL
        ).count(),

        "emergency_changes": Change.objects.filter(
            change_type=Change.EMERGENCY
        ).count(),

        # Dropdown choices
        "change_types": Change.objects.values_list(
            "change_type",
            flat=True
        ).distinct(),

        "status_choices": Change.STATUS_CHOICES,

        "change_type_choices": Change.TYPE_CHOICES,
    }

    return render(
        request,
        "changes/change_list.html",
        context
    )

@login_required
def change_create(request):

    if request.method == "POST":

        form = ChangeForm(request.POST)

        if form.is_valid():

            change = form.save(commit=False)

            # Set the user who requested the change
            change.requested_by = request.user

            # Always start a new RFC in Draft
            change.status = Change.DRAFT

            change.save()

            messages.success(
                request,
                f"Change request {change.change_number} created successfully."
            )

            return redirect(
                "change_detail",
                pk=change.pk
            )

        else:
            # Show validation errors on the page
            messages.error(
                request,
                "Please correct the errors below."
            )

    else:

        form = ChangeForm()

    return render(
        request,
        "changes/change_form.html",
        {
            "form": form
        }
    )

    if request.method == "POST":

        form = ChangeForm(request.POST)

        if form.is_valid():

            change = form.save(commit=False)

            if hasattr(change, "created_by"):
                change.created_by = request.user

            if not change.status:
                change.status = "Draft"

            change.save()

            messages.success(
                request,
                "Change request created successfully."
            )

            return redirect(
                "change_detail",
                pk=change.pk
            )

    else:

        form = ChangeForm()

    return render(
        request,
        "changes/change_form.html",
        {
            "form": form
        }
    )

@login_required
def change_detail(request, pk):

    change = get_object_or_404(
        Change,
        pk=pk
    )

    return render(
        request,
        "changes/change_detail.html",
        {
            "change": change
        }
    )

@login_required
def change_update(request, pk):

    change = get_object_or_404(
        Change,
        pk=pk
    )

    if request.method == "POST":

        form = ChangeForm(
            request.POST,
            instance=change
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Change request updated successfully."
            )

            return redirect(
                "change_detail",
                pk=change.pk
            )

    else:

        form = ChangeForm(
            instance=change
        )

    return render(
        request,
        "changes/change_form.html",
        {
            "form": form,
            "change": change
        }
    )

@login_required
def change_delete(request, pk):

    change = get_object_or_404(
        Change,
        pk=pk
    )

    if request.method == "POST":

        change.delete()

        messages.success(
            request,
            "Change request deleted successfully."
        )

        return redirect(
            "change_list"
        )

    return render(
        request,
        "changes/change_confirm_delete.html",
        {
            "change": change
        }
    )

@login_required
def cab_approval(request, pk):

    change = get_object_or_404(
        Change,
        pk=pk
    )

    if request.method == "POST":

        decision = request.POST.get(
            "decision"
        )

        comments = request.POST.get(
            "comments",
            ""
        )

        scheduled_date = request.POST.get(
            "scheduled_date"
        )

        if decision == "Approved":

            change.status = "Approved"

            if scheduled_date and hasattr(
                change,
                "scheduled_date"
            ):
                change.scheduled_date = scheduled_date

            change.save()

            messages.success(
                request,
                "Change approved by CAB."
            )

        elif decision == "Rejected":

            change.status = "Rejected"

            change.save()

            messages.error(
                request,
                "Change rejected by CAB."
            )

        return redirect(
            "change_detail",
            pk=change.pk
        )

    return render(
        request,
        "changes/cab_approval.html",
        {
            "change": change
        }
    )

@login_required
def change_calendar(request):

    changes = Change.objects.filter(
        scheduled_date__isnull=False
    ).order_by(
        "scheduled_date"
    )

    return render(
        request,
        "changes/change_calendar.html",
        {
            "changes": changes
        }
    )

@login_required
def pir_create(request, pk):

    change = get_object_or_404(
        Change,
        pk=pk
    )

    if request.method == "POST":

        form = PIRForm(
            request.POST
        )

        if form.is_valid():

            pir = form.save(
                commit=False
            )

            pir.change = change
            pir.created_by = request.user
            pir.save()

            change.status = "Closed"
            change.save()

            messages.success(
                request,
                "Post-Implementation Review submitted successfully."
            )

            return redirect(
                "change_detail",
                pk=change.pk
            )

    else:

        form = PIRForm()

    return render(
        request,
        "changes/pir_form.html",
        {
            "form": form,
            "change": change
        }
    )

@login_required
def pir_detail(request, pk):

    pir = get_object_or_404(
        PIR,
        pk=pk
    )

    return render(
        request,
        "changes/pir_detail.html",
        {
            "pir": pir,
            "change": pir.change
        }
    )