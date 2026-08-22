from django.urls import path
from .views import NotificationListView, NotificationDetailView, UnreadCountView

urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path("notifications/<uuid:uuid>/", NotificationDetailView.as_view(), name="notification-detail"),
    path("notifications/unread/count/", UnreadCountView.as_view(), name="notification-unread-count"),
]
