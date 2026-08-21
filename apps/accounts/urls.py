"""
URL routes for accounts app.
"""
from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    APIKeyListView,
    APIKeyDetailView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/profile/", ProfileView.as_view(), name="profile"),
    path("api-keys/", APIKeyListView.as_view(), name="api-key-list"),
    path("api-keys/<uuid:uuid>/", APIKeyDetailView.as_view(), name="api-key-detail"),
]
