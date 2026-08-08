from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from incidents.models import Incident
from .forms import ProblemForm, RCAForm
from .models import Problem, RCA, ProblemHistory, KnownError
from accounts.decorators import role_required
from accounts.models import CustomUser
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth

@login_required
def rca_dashboard(request):

    total_rca = RCA.objects.count()

    draft_rca = RCA.objects.filter(
        status="DRAFT"
    ).count()

    pending_rca = RCA.objects.filter(
        status="PENDING"
    ).count()

    approved_rca = RCA.objects.filter(
        status="APPROVED"
    ).count()


    # RCA Status Chart

    status_data = (
        RCA.objects
        .values("status")
        .annotate(total=Count("id"))
    )

    status_labels = []
    status_values = []

    for item in status_data:
        status_labels.append(item["status"])
        status_values.append(item["total"])



    # RCA Application Chart

    application_data = (
        RCA.objects
        .values("problem__application")
        .annotate(total=Count("id"))
    )

    application_labels = []
    application_values = []

    for item in application_data:
        application_labels.append(
            item["problem__application"]
        )

        application_values.append(
            item["total"]
        )



    # Monthly RCA Trend

    monthly_data = (
        RCA.objects
        .annotate(
            month=TruncMonth("created_at")
        )
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )


    monthly_labels = []
    monthly_values = []


    for item in monthly_data:

        monthly_labels.append(
            item["month"].strftime("%b %Y")
        )

        monthly_values.append(
            item["total"]
        )


    context = {

        "total_rca": total_rca,

        "draft_rca": draft_rca,

        "pending_rca": pending_rca,

        "approved_rca": approved_rca,


        "status_labels": status_labels,

        "status_values": status_values,


        "application_labels": application_labels,

        "application_values": application_values,


        "monthly_labels": monthly_labels,

        "monthly_values": monthly_values,

    }


    return render(
        request,
        "problems/rca_dashboard.html",
        context
    )

@login_required
@role_required([CustomUser.ADMIN])
def delete_problem(request, pk):

    problem = get_object_or_404(
        Problem,
        pk=pk
    )

    if request.method == "POST":

        problem.delete()

        messages.success(
            request,
            "Problem deleted successfully."
        )

        return redirect("problem_list")

    return render(
        request,
        "problems/problem_confirm_delete.html",
        {
            "problem": problem
        }
    )

@login_required
def problem_detail(request, pk):

    problem = get_object_or_404(
        Problem,
        pk=pk
    )

    # Handle form submission
    if request.method == "POST":

        incident_ids = request.POST.getlist("incidents")

        problem.incidents.set(incident_ids)

        # Uncomment if you have a ProblemHistory model
        #ProblemHistory.objects.create(
        #    problem=problem,
        #    user=request.user,
        #    action="Linked incidents updated."
        #)

        messages.success(
            request,
            "Incident links updated successfully."
        )

        return redirect(
            "problem_detail",
            pk=problem.pk
        )

    suggestions = Incident.objects.filter(
        application=problem.application,
        status__in=[
            "OPEN",
            "ASSIGNED",
            "IN_PROGRESS",
        ]
    ).exclude(
        id__in=problem.incidents.values_list(
            "id",
            flat=True
        )
    )

    return render(
        request,
        "problems/problem_detail.html",
        {
            "problem": problem,
            "incidents": Incident.objects.all(),
            "suggestions": suggestions,
        }
    )

@login_required
def problem_list(request):

    problems = Problem.objects.select_related(
        "owner",
        "created_by"
    )

    return render(
        request,
        "problems/problem_list.html",
        {
            "problems": problems
        }
    )

@login_required
def create_problem(request):

    if request.method == "POST":

        form = ProblemForm(request.POST)

        if form.is_valid():

            problem = form.save(commit=False)

            problem.created_by = request.user

            problem.save()

            messages.success(
                request,
                "Problem created successfully."
            )

            return redirect("problem_list")

    else:

        form = ProblemForm()

    return render(
        request,
        "problems/problem_form.html",
        {
            "form": form,
            "title": "Create Problem"
        }
    )

@login_required
def update_problem(request, pk):

    problem = get_object_or_404(
        Problem,
        pk=pk
    )

    if request.method == "POST":

        form = ProblemForm(
            request.POST,
            instance=problem
        )

        if form.is_valid():

            form.save()
            messages.success(
                request,
                "Problem updated successfully."
            )

            return redirect(
                "problem_detail",
                pk=problem.pk
            )

    else:

        form = ProblemForm(
            instance=problem
        )

    return render(
        request,
        "problems/problem_form.html",
        {
            "form": form,
            "title": "Update Problem"
        }
    )

@login_required
def create_known_error(request, problem_id):

    problem = get_object_or_404(
        Problem,
        pk=problem_id
    )

    # Check RCA exists
    if not hasattr(problem, "rca"):

        messages.error(
            request,
            "Complete RCA first."
        )

        return redirect(
            "problem_detail",
            pk=problem.id
        )


    # Check RCA approval status
    if problem.rca.status != RCA.APPROVED:

        messages.error(
            request,
            "RCA must be approved."
        )

        return redirect(
            "problem_detail",
            pk=problem.id
        )


    # Known Error creation logic goes here

    return render(
        request,
        "problems/known_error_form.html",
        {
            "problem": problem
        }
    )


@login_required
def bulk_link_incidents(request, pk):

    problem = get_object_or_404(
        Problem,
        pk=pk
    )

    if request.method == "POST":

        incident_ids = request.POST.getlist(
            "incidents"
        )

        problem.incidents.set(
            incident_ids
        )

        messages.success(
            request,
            "Incidents linked successfully."
        )

        return redirect(
            "problem_detail",
            pk=pk
        )

@login_required
def manage_rca(request, problem_id):

    problem = get_object_or_404(
        Problem,
        pk=problem_id
    )

    rca, created = RCA.objects.get_or_create(

        problem=problem,

        defaults={
            "created_by":request.user
        }

    )

    if request.method == "POST":

        form = RCAForm(

            request.POST,

            instance=rca

        )

        if form.is_valid():

            form.save()

            messages.success(

                request,

                "RCA saved successfully."

            )

            return redirect(

                "problem_detail",

                pk=problem.id

            )

    else:

        form = RCAForm(instance=rca)

    return render(

        request,

        "problems/rca_form.html",

        {

            "form":form,

            "problem":problem

        }

    )

@login_required
def update_rca(request, problem_id):

    problem = get_object_or_404(Problem, id=problem_id)

    rca, created = RCA.objects.get_or_create(
        problem=problem,
        defaults={"created_by": request.user}
    )

    if request.method == "POST":

        form = RCAForm(request.POST, instance=rca)

        if form.is_valid():

            form.save()

            # Add it HERE
            ProblemHistory.objects.create(
                problem=problem,
                user=request.user,
                action="RCA updated."
            )

            messages.success(request, "RCA updated successfully.")

            return redirect("problem_detail", pk=problem.id)

    else:
        form = RCAForm(instance=rca)

    return render(request, "problems/rca_form.html", {"form": form})

@login_required
def rca_detail(request, problem_id):

    problem = get_object_or_404(
        Problem,
        id=problem_id
    )

    rca = get_object_or_404(
        RCA,
        problem=problem
    )

    return render(
        request,
        "problems/rca_detail.html",
        {
            "rca": rca,
            "problem": problem
        }
    )

from django.db.models import Q

def search_kedb(request):

    query = request.GET.get("q", "")

    results = KnownError.objects.filter(

        Q(title__icontains=query) |
        Q(symptoms__icontains=query) |
        Q(keywords__icontains=query) |
        Q(application__icontains=query),

        status=KnownError.ACTIVE

    )

    return render(
        request,
        "kedb/search_results.html",
        {
            "results": results,
            "query": query
        }
    )

@login_required
def search_kedb(request):

    query = request.GET.get("q", "")

    results = KnownError.objects.filter(

        Q(title__icontains=query) |
        Q(symptoms__icontains=query) |
        Q(keywords__icontains=query) |
        Q(application__icontains=query),

        status=KnownError.ACTIVE

    )


    return render(
        request,
        "kedb/search_results.html",
        {
            "results": results,
            "query": query
        }
    )