"""
URL configuration for the SalamaPay payment gateway.
API is versioned under /api/v1/
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "ok", "service": "SalamaPay API", "version": "v1"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", health_check, name="health-check"),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/", include("apps.businesses.urls")),
    path("api/v1/", include("apps.kyc.urls")),
    path("api/v1/", include("apps.wallets.urls")),
    path("api/v1/", include("apps.ledger.urls")),
    path("api/v1/", include("apps.transactions.urls")),
    path("api/v1/", include("apps.fees.urls")),
]
