from django.contrib import admin

from apps.kyc.models import KYCApplication, KYCDocument


@admin.register(KYCApplication)
class KYCApplicationAdmin(admin.ModelAdmin):
    list_display = ("business", "applicant", "type", "status", "reviewed_by", "submitted_at", "reviewed_at")
    list_filter = ("status", "type")
    search_fields = ("business__name", "applicant__email")
    readonly_fields = ("uuid", "submitted_at", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ("document_type", "kyc_application", "status", "verified_at", "created_at")
    list_filter = ("document_type", "status")
    search_fields = ("document_number", "kyc_application__business__name")
    readonly_fields = ("uuid", "verified_at", "created_at", "updated_at")
    ordering = ("-created_at",)
