from django.contrib import admin
from apps.developer.models import APIRequestLog, RateLimitTracker


@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    list_display = ("request_id", "method", "path", "status_code", "response_time_ms", "business", "created_at")
    list_filter = ("method", "status_code", "environment")
    search_fields = ("request_id", "path", "client_ip")
    readonly_fields = ("uuid", "created_at")
    ordering = ["-created_at"]


@admin.register(RateLimitTracker)
class RateLimitTrackerAdmin(admin.ModelAdmin):
    list_display = ("identifier", "request_count", "request_limit", "is_exceeded", "window_start", "updated_at")
    list_filter = ()
    search_fields = ("identifier",)
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ["-updated_at"]
