from datetime import timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    ServiceRequest,
    ServiceCatalog,
    ServiceRequestApproval,
    ServiceRequestComment,
    ServiceRequestAttachment,
)


User = get_user_model()


# ============================================================
# SERVICE REQUEST CREATE FORM
# ============================================================

class ServiceRequestForm(forms.ModelForm):

    class Meta:

        model = ServiceRequest

        fields = [
            "service",
            "title",
            "description",
            "category",
            "subcategory",
            "requester",
            "assigned_to",
            "priority",
            "status",
            "sla_due_at",
            "sla_breached",
            "resolved_at",
            "closed_at",
        ]

        widgets = {

            # ------------------------------------------------
            # Service
            # ------------------------------------------------

            "service": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_service",
                }
            ),

            # ------------------------------------------------
            # Title
            # ------------------------------------------------

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter request title",
                }
            ),

            # ------------------------------------------------
            # Description
            # ------------------------------------------------

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe the service request",
                }
            ),

            # ------------------------------------------------
            # Category
            # ------------------------------------------------

            "category": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                }
            ),

            # ------------------------------------------------
            # Subcategory
            # ------------------------------------------------

            "subcategory": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                }
            ),

            # ------------------------------------------------
            # Requester
            # ------------------------------------------------

            "requester": forms.Select(
                attrs={
                    "class": "form-select",
                    "disabled": "disabled",
                }
            ),

            # ------------------------------------------------
            # Assigned To
            # ------------------------------------------------

            "assigned_to": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            # ------------------------------------------------
            # Priority
            # ------------------------------------------------

            "priority": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            # ------------------------------------------------
            # Status
            # ------------------------------------------------

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                    "disabled": "disabled",
                }
            ),

            # ------------------------------------------------
            # SLA Due At
            # ------------------------------------------------

            "sla_due_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                    "readonly": "readonly",
                }
            ),

            # ------------------------------------------------
            # SLA Breached
            # ------------------------------------------------

            "sla_breached": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "disabled": "disabled",
                }
            ),

            # ------------------------------------------------
            # Resolved At
            # ------------------------------------------------

            "resolved_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                    "readonly": "readonly",
                }
            ),

            # ------------------------------------------------
            # Closed At
            # ------------------------------------------------

            "closed_at": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                    "readonly": "readonly",
                }
            ),
        }


    def __init__(
        self,
        *args,
        user=None,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        self.user = user

        # ----------------------------------------------------
        # Active services only
        # ----------------------------------------------------

        self.fields["service"].choices = [
            ("", "---------")
        ] + [
            (
                service.pk,
                service.name
            )
            for service in ServiceCatalog.objects.filter(
                is_active=True
            )
        ]


        # ----------------------------------------------------
        # Requester
        # ----------------------------------------------------

        self.fields["requester"].queryset = (
            User.objects.all()
        )

        self.fields["requester"].required = False

        if user:

            self.fields["requester"].initial = user.pk


        # ----------------------------------------------------
        # Assigned engineers / team members
        # ----------------------------------------------------

        self.fields["assigned_to"].queryset = (
            User.objects.filter(
                role__in=[
                    "SUPPORT",
                ]
            )
        )

        self.fields["assigned_to"].required = False


        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        self.fields["status"].initial = (
            ServiceRequest.DRAFT
        )

        self.fields["status"].disabled = True


        # ----------------------------------------------------
        # SLA fields
        # ----------------------------------------------------

        self.fields["sla_due_at"].required = False
        self.fields["sla_breached"].required = False
        self.fields["resolved_at"].required = False
        self.fields["closed_at"].required = False


        # ----------------------------------------------------
        # Initial SLA state
        # ----------------------------------------------------

        self.fields["sla_breached"].initial = False


        # ----------------------------------------------------
        # New request should not have these timestamps
        # ----------------------------------------------------

        self.fields["resolved_at"].initial = None
        self.fields["closed_at"].initial = None


    def clean(self):

        cleaned_data = super().clean()

        service = cleaned_data.get("service")


        # ----------------------------------------------------
        # Automatically populate Service-related fields
        # ----------------------------------------------------

        if service:

            cleaned_data["category"] = (
                service.category
            )

            cleaned_data["subcategory"] = (
                service.subcategory
            )

            cleaned_data["priority"] = (
                service.default_priority
            )


        # ----------------------------------------------------
        # New requests always start as Draft
        # ----------------------------------------------------

        cleaned_data["status"] = (
            ServiceRequest.DRAFT
        )


        # ----------------------------------------------------
        # SLA calculation
        # ----------------------------------------------------

        if service:

            cleaned_data["sla_due_at"] = (
                timezone.now()
                + timedelta(
                    hours=service.sla_hours
                )
            )


        # ----------------------------------------------------
        # New request is not breached
        # ----------------------------------------------------

        cleaned_data["sla_breached"] = False


        # ----------------------------------------------------
        # New request is not resolved or closed
        # ----------------------------------------------------

        cleaned_data["resolved_at"] = None
        cleaned_data["closed_at"] = None


        return cleaned_data


    def save(self, commit=True):

        instance = super().save(
            commit=False
        )


        # ----------------------------------------------------
        # Automatically set requester
        # ----------------------------------------------------

        if self.user:

            instance.requester = self.user


        # ----------------------------------------------------
        # New request starts as Draft
        # ----------------------------------------------------

        instance.status = (
            ServiceRequest.DRAFT
        )


        # ----------------------------------------------------
        # Automatically calculate SLA
        # ----------------------------------------------------

        if instance.service:

            instance.sla_due_at = (
                timezone.now()
                + timedelta(
                    hours=instance.service.sla_hours
                )
            )


        # ----------------------------------------------------
        # New request is not breached
        # ----------------------------------------------------

        instance.sla_breached = False


        # ----------------------------------------------------
        # New request cannot already be resolved/closed
        # ----------------------------------------------------

        instance.resolved_at = None
        instance.closed_at = None


        if commit:

            instance.save()


        return instance


# ============================================================
# SERVICE REQUEST UPDATE FORM
# ============================================================

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

            # ------------------------------------------------
            # Title
            # ------------------------------------------------

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            # ------------------------------------------------
            # Description
            # ------------------------------------------------

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                }
            ),

            # ------------------------------------------------
            # Priority
            # ------------------------------------------------

            "priority": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            # ------------------------------------------------
            # Assigned To
            # ------------------------------------------------

            "assigned_to": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            # ------------------------------------------------
            # Status
            # ------------------------------------------------

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }


    def __init__(
        self,
        *args,
        user=None,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.user = user


        # ----------------------------------------------------
        # Assigned users
        # ----------------------------------------------------

        self.fields["assigned_to"].queryset = (
            User.objects.filter(
                role__in=[
                    "SUPPORT",
                ]
            )
        )

        self.fields["assigned_to"].required = False


        # ----------------------------------------------------
        # Role-based restrictions
        # ----------------------------------------------------

        if user:

            user_role = getattr(
                user,
                "role",
                None
            )


            # ----------------------------------------------
            # Only Admin / Team Lead can change:
            # - Assignment
            # - Status
            # ----------------------------------------------

            if user_role not in [
                "ADMIN",
                "TEAM_LEAD",
            ]:

                self.fields[
                    "assigned_to"
                ].disabled = True

                self.fields[
                    "status"
                ].disabled = True


# ============================================================
# SERVICE REQUEST COMMENT FORM
# ============================================================

class ServiceRequestCommentForm(
    forms.ModelForm
):

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


# ============================================================
# SERVICE REQUEST ATTACHMENT FORM
# ============================================================

class ServiceRequestAttachmentForm(
    forms.ModelForm
):

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


# ============================================================
# SERVICE REQUEST APPROVAL FORM
# ============================================================

class ServiceRequestApprovalForm(
    forms.Form
):

    DECISION_CHOICES = [

        (
            ServiceRequestApproval.APPROVED,
            "Approve",
        ),

        (
            ServiceRequestApproval.REJECTED,
            "Reject",
        ),
    ]


    # --------------------------------------------------------
    # Approval decision
    # --------------------------------------------------------

    decision = forms.ChoiceField(

        choices=DECISION_CHOICES,

        widget=forms.RadioSelect,

        required=True,
    )


    # --------------------------------------------------------
    # Approval comments
    # --------------------------------------------------------

    comments = forms.CharField(

        required=False,

        widget=forms.Textarea(

            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": (
                    "Enter approval/rejection comments..."
                ),
            }
        ),
    )