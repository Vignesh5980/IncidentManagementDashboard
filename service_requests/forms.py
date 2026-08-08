from django import forms
from .models import ServiceRequest, ServiceCatalog, ServiceRequestComment, ServiceRequestAttachment
from django.contrib.auth import get_user_model

User = get_user_model()

class ServiceRequestForm(forms.ModelForm):

    class Meta:
        model = ServiceRequest

        fields = [
            "title",
            "description",
            "service",
            "category",
            "subcategory",
            "priority",
            "requester",
            "assigned_to",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter request title",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe the service request",
                }
            ),

            "service": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "category": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "subcategory": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "priority": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "requester": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "assigned_to": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }


    def clean(self):

        cleaned_data = super().clean()

        service = cleaned_data.get("service")

        if service:

            cleaned_data["category"] = service.category

            cleaned_data["subcategory"] = service.subcategory

            cleaned_data["priority"] = service.default_priority

        return cleaned_data


class ServiceRequestUpdateForm(forms.ModelForm):

    class Meta:
        model = ServiceRequest

        fields = [
            "title",
            "description",
            "priority",
            "assigned_to",
            "status",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                }
            ),

            "priority": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "assigned_to": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.user = user

        self.fields["assigned_to"].queryset = (
            User.objects.filter(
                role__in=[
                    "ADMIN",
                    "TEAM_LEAD",
                    "SUPPORT_ENGINEER",
                ]
            )
        )

        # Support Engineers cannot change
        # assignment or status directly.
        if user and getattr(user, "role", None) not in [
            "ADMIN",
            "TEAM_LEAD",
        ]:

            self.fields["assigned_to"].disabled = True
            self.fields["status"].disabled = True

class ServiceRequestCommentForm(forms.ModelForm):

    class Meta:
        model = ServiceRequestComment

        fields = [
            "comment",
        ]

        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Add a comment...",
                }
            ),
        }


class ServiceRequestAttachmentForm(forms.ModelForm):

    class Meta:
        model = ServiceRequestAttachment

        fields = [
            "file",
        ]

        widgets = {
            "file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }