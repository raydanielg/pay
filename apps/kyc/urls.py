"""
URL routes for KYC app.
"""
from django.urls import path

from .views import (
    KYCApplicationListCreateView,
    KYCApplicationDetailView,
    KYCDocumentListCreateView,
    KYCReviewView,
)

urlpatterns = [
    path("kyc/", KYCApplicationListCreateView.as_view(), name="kyc-list"),
    path("kyc/<uuid:uuid>/", KYCApplicationDetailView.as_view(), name="kyc-detail"),
    path("kyc/<uuid:application_uuid>/documents/", KYCDocumentListCreateView.as_view(), name="kyc-document-list"),
    path("kyc/<uuid:uuid>/review/", KYCReviewView.as_view(), name="kyc-review"),
]
