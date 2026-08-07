from django import forms
from .models import Problem
from incidents.models import Incident
from accounts.models import CustomUser
from .models import RCA


class RCAForm(forms.ModelForm):

    class Meta:
        model = RCA
        fields = "__all__"
        exclude = ["problem", "created_by"]

        widgets = {
            "summary": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "root_cause": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "impact": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "corrective_action": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "preventive_action": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "why1": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "why2": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "why3": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "why4": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "why5": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "people": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "process": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "technology": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "environment": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "measurement": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

class ProblemForm(forms.ModelForm):

    incidents = forms.ModelMultipleChoiceField(
        queryset=Incident.objects.filter(
            status__in=[
                "OPEN",
                "ASSIGNED",
                "IN_PROGRESS",
            ]
        ),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = Problem

        fields = [
            "title",
            "description",
            "application",
            "owner",
            "status",
            "incidents",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),
            "application": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "owner": forms.Select(attrs={
                "class": "form-select"
            }),
            "status": forms.Select(attrs={
                "class": "form-select"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["owner"].queryset = CustomUser.objects.filter(
            role__in=[
                CustomUser.ADMIN,
                CustomUser.TEAM_LEAD,
            ]
        )