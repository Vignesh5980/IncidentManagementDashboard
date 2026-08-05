from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def incident_list(request):
    return render(request, "incidents/incident_list.html")