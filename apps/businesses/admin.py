from django.contrib import admin

from apps.businesses.models import Business, BusinessMember


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "country", "currency", "status", "kyc_status", "can_receive_payments", "created_at")
    list_filter = ("status", "kyc_status", "country", "currency")
    search_fields = ("name", "legal_name", "registration_number", "tin", "owner__email")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(BusinessMember)
class BusinessMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "business", "role", "is_active", "joined_at", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("user__email", "business__name")
    readonly_fields = ("uuid", "invited_at", "joined_at", "created_at", "updated_at")
    ordering = ("-created_at",)
