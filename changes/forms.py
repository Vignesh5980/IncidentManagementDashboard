from django import forms
from .models import Change, PIR


class ChangeForm(forms.ModelForm):

    class Meta:
        model = Change

        fields = [
            "title",
            "description",
            "change_type",
            "status",
            "application",
            "assigned_to",
            "scheduled_start",
            "scheduled_end",
            "implementation_plan",
            "rollback_plan",
            "risk",
            "impact",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter change title"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the change"
                }
            ),

            "change_type": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "application": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Application / Service name"
                }
            ),

            "assigned_to": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "scheduled_start": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),

            "scheduled_end": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),

            "implementation_plan": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe the implementation steps"
                }
            ),

            "rollback_plan": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe the rollback / backout procedure"
                }
            ),

            "risk": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the risks associated with this change"
                }
            ),

            "impact": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the business / service impact"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Change number is generated automatically.
        # Requested user is assigned in the view.
        # Assigned-to can be selected by the user.

        self.fields["assigned_to"].required = False

        # For a new RFC, start with Draft.
        if not self.instance.pk:
            self.fields["status"].initial = Change.DRAFT


class PIRForm(forms.ModelForm):

    class Meta:
        model = PIR

        fields = [
            "successful",
            "observations",
            "lessons",
            "recommendations",
        ]

        widgets = {
            "successful": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),

            "observations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe what happened during implementation..."
                }
            ),

            "lessons": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "What did the team learn from this change?"
                }
            ),

            "recommendations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Enter recommendations or corrective actions..."
                }
            ),
        }
