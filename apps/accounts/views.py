"""
Views for accounts — registration, profile, and API key management.
"""
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import User, APIKey
from apps.accounts.serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    APIKeySerializer,
    APIKeyCreateSerializer,
)
from common.utilities.responses import success_response, error_response


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserProfileSerializer(user).data
        return success_response(
            data=data,
            message="Account created successfully. Please verify your email.",
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """JWT login — returns access and refresh tokens."""
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Profile retrieved")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Profile updated")


class APIKeyListView(generics.ListCreateAPIView):
    """List and create API keys for the authenticated user's business."""
    permission_classes = [IsAuthenticated]

    def get_business(self):
        from apps.businesses.models import Business
        return Business.objects.filter(owner=self.request.user).first()

    def get_queryset(self):
        business = self.get_business()
        if not business:
            return APIKey.objects.none()
        return APIKey.objects.filter(business=business)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return APIKeyCreateSerializer
        return APIKeySerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["business"] = self.get_business()
        return ctx

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="API keys retrieved")

    def create(self, request, *args, **kwargs):
        business = self.get_business()
        if not business:
            return error_response(
                message="No business found for this account",
                error_code="NO_BUSINESS",
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            data=serializer.data,
            message="API key created successfully",
            status=status.HTTP_201_CREATED,
        )


class APIKeyDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or revoke an API key."""
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from apps.businesses.models import Business
        business = Business.objects.filter(owner=self.request.user).first()
        if not business:
            return APIKey.objects.none()
        return APIKey.objects.filter(business=business)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="API key retrieved")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return success_response(message="API key revoked")
