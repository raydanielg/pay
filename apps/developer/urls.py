from django.urls import path
from .views import APIRequestLogListView, APIRequestLogDetailView

urlpatterns = [
    path("developer/api-logs/", APIRequestLogListView.as_view(), name="api-log-list"),
    path("developer/api-logs/<uuid:uuid>/", APIRequestLogDetailView.as_view(), name="api-log-detail"),
]
