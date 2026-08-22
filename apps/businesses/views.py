"""
Views for businesses — CRUD for business and members.
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apps.businesses.models import Business, BusinessMember
from apps.businesses.serializers import BusinessSerializer, BusinessMemberSerializer
from common.utilities.responses import success_response, error_response


class BusinessListCreateView(generics.ListCreateAPIView):
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Business.objects.filter(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Businesses retrieved")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        business = serializer.save()
        from apps.rbac.models import Role
        from django.utils import timezone
        owner_role = Role.objects.get(code="BUSINESS_OWNER")
        BusinessMember.objects.create(
            business=business,
            user=request.user,
            role=owner_role,
            joined_at=timezone.now(),
        )
        data = BusinessSerializer(business).data
        return success_response(
            data=data,
            message="Business created successfully",
            status=status.HTTP_201_CREATED,
        )


class BusinessDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        return Business.objects.filter(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Business retrieved")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Business updated")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = "suspended"
        instance.save()
        return success_response(message="Business suspended")


class BusinessMemberListView(generics.ListCreateAPIView):
    serializer_class = BusinessMemberSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_business(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Business, uuid=self.kwargs["business_uuid"], owner=self.request.user)

    def get_queryset(self):
        return BusinessMember.objects.filter(business=self.get_business())

    def create(self, request, *args, **kwargs):
        business = self.get_business()
        from apps.accounts.models import User
        email = request.data.get("email")
        if not email:
            return error_response(message="Email is required", error_code="EMAIL_REQUIRED", status=400)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response(message="User not found", error_code="USER_NOT_FOUND", status=404)

        from apps.rbac.models import Role
        role_code = request.data.get("role_code", "DEVELOPER")
        try:
            role = Role.objects.get(code=role_code, category="business", is_active=True)
        except Role.DoesNotExist:
            return error_response(message=f"Role {role_code} not found", error_code="ROLE_NOT_FOUND", status=404)

        member, created = BusinessMember.objects.get_or_create(
            business=business,
            user=user,
            defaults={"role": role},
        )
        if not created:
            return error_response(message="User is already a member", error_code="ALREADY_MEMBER", status=409)

        serializer = self.get_serializer(member)
        return success_response(data=serializer.data, message="Member added", status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Members retrieved")


class BusinessMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessMemberSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        return BusinessMember.objects.filter(business__owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Member retrieved")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Member updated")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.role.code == "BUSINESS_OWNER":
            return error_response(message="Cannot remove business owner", error_code="CANNOT_REMOVE_OWNER", status=400)
        instance.is_active = False
        instance.save()
        return success_response(message="Member removed")
