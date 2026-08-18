from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from incidents.tests.base import BaseAPITestCase

from service_requests.forms import (
    ServiceRequestForm,
    ServiceRequestUpdateForm,
    ServiceRequestCommentForm,
    ServiceRequestAttachmentForm,
    ServiceRequestApprovalForm,
)

from service_requests.models import (
    ServiceRequest,
    ServiceCatalog,
    ServiceRequestComment,
    ServiceRequestAttachment,
    ServiceRequestApproval,
)


class ServiceRequestFormTests(BaseAPITestCase):

    def setUp(self):
        super().setUp()

        self.service = ServiceCatalog.objects.create(
            name="Laptop Support",
            category="Hardware",
            subcategory="Laptop",
            default_priority="P2",
            sla_hours=4,
            is_active=True,
        )

        self.inactive_service = ServiceCatalog.objects.create(
            name="Inactive Service",
            category="Software",
            subcategory="Installation",
            default_priority="P3",
            sla_hours=8,
            is_active=False,
        )

    # =========================================================
    # SERVICE REQUEST FORM
    # =========================================================

    def test_service_request_form_initializes_active_services(self):

        form = ServiceRequestForm(
            user=self.admin_user
        )

        service_choices = list(
            form.fields["service"].choices
        )

        self.assertIn(
            (
                self.service.pk,
                self.service.name
            ),
            service_choices
        )

        self.assertNotIn(
            (
                self.inactive_service.pk,
                self.inactive_service.name
            ),
            service_choices
        )

    def test_service_request_form_initializes_requester(self):

        form = ServiceRequestForm(
            user=self.admin_user
        )

        self.assertEqual(
            form.fields["requester"].initial,
            self.admin_user.pk
        )

        self.assertFalse(
            form.fields["requester"].required
        )

    def test_service_request_form_without_user(self):

        form = ServiceRequestForm()

        self.assertIsNone(
            form.fields["requester"].initial
        )

        self.assertFalse(
            form.fields["requester"].required
        )

    def test_service_request_form_assigned_to_support_users(self):

        form = ServiceRequestForm(
            user=self.admin_user
        )

        assigned_queryset = (
            form.fields["assigned_to"].queryset
        )

        self.assertIn(
            self.support_engineer,
            assigned_queryset
        )

        self.assertNotIn(
            self.admin_user,
            assigned_queryset
        )

        self.assertNotIn(
            self.team_lead,
            assigned_queryset
        )

    def test_service_request_form_initializes_status(self):

        form = ServiceRequestForm(
            user=self.admin_user
        )

        self.assertEqual(
            form.fields["status"].initial,
            ServiceRequest.DRAFT
        )

        self.assertTrue(
            form.fields["status"].disabled
        )

    def test_service_request_form_initializes_sla_fields(self):

        form = ServiceRequestForm(
            user=self.admin_user
        )

        self.assertFalse(
            form.fields["sla_due_at"].required
        )

        self.assertFalse(
            form.fields["sla_breached"].required
        )

        self.assertFalse(
            form.fields["resolved_at"].required
        )

        self.assertFalse(
            form.fields["closed_at"].required
        )

        self.assertFalse(
            form.fields["sla_breached"].initial
        )

        self.assertIsNone(
            form.fields["resolved_at"].initial
        )

        self.assertIsNone(
            form.fields["closed_at"].initial
        )

    # =========================================================
    # CLEAN
    # =========================================================

    def test_service_request_form_clean_populates_service_fields(self):

        form = ServiceRequestForm(
            data={
                "service": self.service.pk,
                "title": "Laptop Request",
                "description": "Need a new laptop",
                "requester": self.admin_user.pk,
                "assigned_to": self.support_engineer.pk,
                "priority": "P1",
                "status": "SUBMITTED",
            },
            user=self.admin_user,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors
        )

        cleaned_data = form.cleaned_data

        self.assertEqual(
            cleaned_data["category"],
            self.service.category
        )

        self.assertEqual(
            cleaned_data["subcategory"],
            self.service.subcategory
        )

        self.assertEqual(
            cleaned_data["priority"],
            self.service.default_priority
        )

        self.assertEqual(
            cleaned_data["status"],
            ServiceRequest.DRAFT
        )

        self.assertFalse(
            cleaned_data["sla_breached"]
        )

        self.assertIsNone(
            cleaned_data["resolved_at"]
        )

        self.assertIsNone(
            cleaned_data["closed_at"]
        )

        self.assertIsNotNone(
            cleaned_data["sla_due_at"]
        )

    def test_service_request_form_clean_calculates_sla(self):

        before = timezone.now()

        form = ServiceRequestForm(
            data={
                "service": self.service.pk,
                "title": "SLA Test",
                "description": "Testing SLA calculation",
                "requester": self.admin_user.pk,
                "priority": "P2",
                "status": "SUBMITTED",
            },
            user=self.admin_user,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors
        )

        after = timezone.now()

        sla_due_at = form.cleaned_data[
            "sla_due_at"
        ]

        expected_min = (
            before
            + timedelta(hours=self.service.sla_hours)
        )

        expected_max = (
            after
            + timedelta(hours=self.service.sla_hours)
        )

        self.assertGreaterEqual(
            sla_due_at,
            expected_min
        )

        self.assertLessEqual(
            sla_due_at,
            expected_max
        )

    def test_service_request_form_clean_without_service(self):

        form = ServiceRequestForm(
            data={
                "service": "",
                "title": "No Service Request",
                "description": "Request without service",
                "requester": self.admin_user.pk,
                "priority": "P2",
                "status": "SUBMITTED",
            },
            user=self.admin_user,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors
        )

        cleaned_data = form.cleaned_data

        self.assertEqual(
            cleaned_data["status"],
            ServiceRequest.DRAFT
        )

        self.assertFalse(
            cleaned_data["sla_breached"]
        )

        self.assertIsNone(
            cleaned_data["sla_due_at"]
        )

        self.assertIsNone(
            cleaned_data["resolved_at"]
        )

        self.assertIsNone(
            cleaned_data["closed_at"]
        )

    # =========================================================
    # SAVE
    # =========================================================

    def test_service_request_form_save_sets_requester(self):

        form = ServiceRequestForm(
            data={
                "service": self.service.pk,
                "title": "Save Test",
                "description": "Testing save",
                "requester": self.admin_user.pk,
                "priority": "P2",
                "status": "SUBMITTED",
            },
            user=self.admin_user,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors
        )

        instance = form.save()

        self.assertIsNotNone(
            instance.pk
        )

        self.assertEqual(
            instance.requester,
            self.admin_user
        )

        self.assertEqual(
            instance.status,
            ServiceRequest.DRAFT
        )

        self.assertFalse(
            instance.sla_breached
        )

        self.assertIsNone(
            instance.resolved_at
        )

        self.assertIsNone(
            instance.closed_at
        )

        self.assertIsNotNone(
            instance.sla_due_at
        )

    def test_service_request_form_save_commit_false(self):

        form = ServiceRequestForm(
            data={
                "service": self.service.pk,
                "title": "Commit False Test",
                "description": "Testing commit false",
                "requester": self.admin_user.pk,
                "priority": "P2",
                "status": "SUBMITTED",
            },
            user=self.admin_user,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors
        )

        instance = form.save(
            commit=False
        )

        self.assertIsNone(
            instance.pk
        )

        self.assertEqual(
            instance.requester,
            self.admin_user
        )

        self.assertEqual(
            instance.status,
            ServiceRequest.DRAFT
        )

        self.assertFalse(
            instance.sla_breached
        )

    # =========================================================
    # UPDATE FORM
    # =========================================================

    def test_update_form_initializes_assigned_users(self):

        form = ServiceRequestUpdateForm(
            user=self.admin_user
        )

        assigned_queryset = (
            form.fields["assigned_to"].queryset
        )

        self.assertIn(
            self.support_engineer,
            assigned_queryset
        )

        self.assertNotIn(
            self.admin_user,
            assigned_queryset
        )

    def test_update_form_admin_can_change_assignment_and_status(self):

        form = ServiceRequestUpdateForm(
            user=self.admin_user
        )

        self.assertFalse(
            form.fields["assigned_to"].disabled
        )

        self.assertFalse(
            form.fields["status"].disabled
        )

    def test_update_form_team_lead_can_change_assignment_and_status(self):

        form = ServiceRequestUpdateForm(
            user=self.team_lead
        )

        self.assertFalse(
            form.fields["assigned_to"].disabled
        )

        self.assertFalse(
            form.fields["status"].disabled
        )

    def test_update_form_support_engineer_cannot_change_assignment_and_status(self):

        form = ServiceRequestUpdateForm(
            user=self.support_engineer
        )

        self.assertTrue(
            form.fields["assigned_to"].disabled
        )

        self.assertTrue(
            form.fields["status"].disabled
        )

    def test_update_form_without_user(self):

        form = ServiceRequestUpdateForm()

        self.assertFalse(
            form.fields["assigned_to"].disabled
        )

        self.assertFalse(
            form.fields["status"].disabled
        )

    # =========================================================
    # COMMENT FORM
    # =========================================================

    def test_service_request_comment_form(self):

        form = ServiceRequestCommentForm()

        self.assertIn(
            "comment",
            form.fields
        )

        self.assertEqual(
            form.fields["comment"].widget.attrs["rows"],
            4
        )

        self.assertEqual(
            form.fields["comment"].widget.attrs["class"],
            "form-control"
        )

    # =========================================================
    # ATTACHMENT FORM
    # =========================================================

    def test_service_request_attachment_form(self):

        form = ServiceRequestAttachmentForm()

        self.assertIn(
            "file",
            form.fields
        )

        self.assertEqual(
            form.fields["file"].widget.attrs["class"],
            "form-control"
        )

    def test_service_request_attachment_form_accepts_file(self):

        uploaded_file = SimpleUploadedFile(
            "test.txt",
            b"Test attachment content",
            content_type="text/plain",
        )

        form = ServiceRequestAttachmentForm(
            files={
                "file": uploaded_file
            }
        )

        self.assertTrue(
            form.is_valid(),
            form.errors
        )

    # =========================================================
    # APPROVAL FORM
    # =========================================================

    def test_approval_form_has_decision_choices(self):

        form = ServiceRequestApprovalForm()

        self.assertEqual(
            form.fields["decision"].choices,
            ServiceRequestApprovalForm.DECISION_CHOICES
        )

    def test_approval_form_requires_decision(self):

        form = ServiceRequestApprovalForm(
            data={
                "comments": "Please review this request."
            }
        )

        self.assertFalse(
            form.is_valid()
        )

        self.assertIn(
            "decision",
            form.errors
        )

    def test_approval_form_accepts_approved_decision(self):

        form = ServiceRequestApprovalForm(
            data={
                "decision": ServiceRequestApproval.APPROVED,
                "comments": "Approved by administrator.",
            }
        )

        self.assertTrue(
            form.is_valid(),
            form.errors
        )

        self.assertEqual(
            form.cleaned_data["decision"],
            ServiceRequestApproval.APPROVED
        )

    def test_approval_form_accepts_rejected_decision(self):

        form = ServiceRequestApprovalForm(
            data={
                "decision": ServiceRequestApproval.REJECTED,
                "comments": "Request rejected.",
            }
        )

        self.assertTrue(
            form.is_valid(),
            form.errors
        )

        self.assertEqual(
            form.cleaned_data["decision"],
            ServiceRequestApproval.REJECTED
        )

    def test_approval_form_comments_are_optional(self):

        form = ServiceRequestApprovalForm(
            data={
                "decision": ServiceRequestApproval.APPROVED
            }
        )

        self.assertTrue(
            form.is_valid(),
            form.errors
        )

        self.assertEqual(
            form.cleaned_data["comments"],
            ""
        )