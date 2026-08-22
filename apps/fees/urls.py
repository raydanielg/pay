"""
URL routes for fees app.
"""
from django.urls import path

from .views import FeeRuleListView, FeeRuleDetailView, FeeCalculateView

urlpatterns = [
    path("fees/rules/", FeeRuleListView.as_view(), name="fee-rule-list"),
    path("fees/rules/<uuid:uuid>/", FeeRuleDetailView.as_view(), name="fee-rule-detail"),
    path("fees/calculate/", FeeCalculateView.as_view(), name="fee-calculate"),
]
