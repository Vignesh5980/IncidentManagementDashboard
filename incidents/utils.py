from django.db.models import Q


def filter_incidents(request, queryset):

    priority = request.GET.get("priority")
    status = request.GET.get("status")
    application = request.GET.get("application")
    engineer = request.GET.get("engineer")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    keyword = request.GET.get("keyword")

    if priority:
        queryset = queryset.filter(priority=priority)

    if status:
        queryset = queryset.filter(status=status)

    if application:
        queryset = queryset.filter(application=application)

    if engineer:
        queryset = queryset.filter(assigned_to_id=engineer)

    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)

    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)

    if keyword:
        queryset = queryset.filter(
            Q(incident_number__icontains=keyword) |
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword)
        )

    return queryset