"""
URL routes for businesses app.
"""
from django.urls import path

from .views import (
    BusinessListCreateView,
    BusinessDetailView,
    BusinessMemberListView,
    BusinessMemberDetailView,
)

urlpatterns = [
    path("businesses/", BusinessListCreateView.as_view(), name="business-list"),
    path("businesses/<uuid:uuid>/", BusinessDetailView.as_view(), name="business-detail"),
    path("businesses/<uuid:business_uuid>/members/", BusinessMemberListView.as_view(), name="business-member-list"),
    path("businesses/<uuid:business_uuid>/members/<uuid:uuid>/", BusinessMemberDetailView.as_view(), name="business-member-detail"),
]
