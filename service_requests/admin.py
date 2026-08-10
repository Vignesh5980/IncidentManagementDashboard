from django.contrib import admin

from .models import (
    ServiceCatalog,
    ServiceRequest,
    ServiceRequestComment,
    ServiceRequestAttachment,
    ServiceRequestApproval,
)

@admin.register(ServiceCatalog)
class ServiceCatalogAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "subcategory",
        "default_priority",
        "sla_hours",
        "requires_approval",
        "is_active",
    )

    list_filter = (
        "category",
        "default_priority",
        "requires_approval",
        "is_active",
    )

    search_fields = (
        "name",
        "category",
        "subcategory",
    )

    
@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):

    list_display = (
        "request_number",
        "title",
        "category",
        "priority",
        "status",
        "requester",
        "assigned_to",
        "created_at",
    )

    list_filter = (
        "priority",
        "status",
        "category",
    )

    search_fields = (
        "request_number",
        "title",
        "description",
        "category",
    )


@admin.register(ServiceRequestComment)
class ServiceRequestCommentAdmin(admin.ModelAdmin):

    list_display = (
        "service_request",
        "user",
        "created_at",
    )


@admin.register(ServiceRequestAttachment)
class ServiceRequestAttachmentAdmin(admin.ModelAdmin):

    list_display = (
        "service_request",
        "file",
        "uploaded_by",
        "uploaded_at",
    )


@admin.register(ServiceRequestApproval)
class ServiceRequestApprovalAdmin(admin.ModelAdmin):

    list_display = (
        "service_request",
        "approver",
        "status",
    )

    list_filter = (
        "status",
    )