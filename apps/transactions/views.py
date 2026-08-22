"""
Views for transactions — list, retrieve, create, and customer management.
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from apps.transactions.models import Transaction, Customer
from apps.transactions.serializers import (
    TransactionSerializer,
    TransactionCreateSerializer,
    CustomerSerializer,
)
from apps.transactions.services import TransactionService
from common.utilities.responses import success_response, error_response


class TransactionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(business__owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TransactionCreateSerializer
        return TransactionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Transactions retrieved")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.businesses.models import Business
        from apps.wallets.models import Wallet

        business = Business.objects.filter(owner=request.user).first()
        if not business:
            return error_response(message="No business found", error_code="NO_BUSINESS", status=404)

        wallet = serializer.validated_data.get("wallet")
        if wallet and wallet.business.owner != request.user:
            return error_response(message="Wallet does not belong to your business", error_code="WALLET_MISMATCH", status=403)

        try:
            txn = TransactionService.create_transaction(
                business=business,
                wallet=wallet,
                amount=serializer.validated_data["amount"],
                currency=serializer.validated_data.get("currency", "TZS"),
                type=serializer.validated_data.get("type", "payment"),
                external_reference=serializer.validated_data.get("external_reference", ""),
                customer=serializer.validated_data.get("customer"),
                description=serializer.validated_data.get("description", ""),
                metadata=serializer.validated_data.get("metadata", {}),
                idempotency_key=serializer.validated_data.get("idempotency_key", ""),
            )
        except Exception as e:
            return error_response(
                message=str(e),
                error_code=getattr(e, "code", "TRANSACTION_ERROR"),
                status=400,
            )

        data = TransactionSerializer(txn).data
        return success_response(data=data, message="Transaction created", status=status.HTTP_201_CREATED)


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        return Transaction.objects.filter(business__owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Transaction retrieved")


class CustomerListCreateView(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from apps.businesses.models import Business
        business = Business.objects.filter(owner=self.request.user).first()
        if not business:
            return Customer.objects.none()
        return Customer.objects.filter(business=business)

    def perform_create(self, serializer):
        from apps.businesses.models import Business
        business = Business.objects.filter(owner=self.request.user).first()
        serializer.save(business=business)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Customers retrieved")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(data=serializer.data, message="Customer created", status=status.HTTP_201_CREATED)


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        from apps.businesses.models import Business
        business = Business.objects.filter(owner=self.request.user).first()
        if not business:
            return Customer.objects.none()
        return Customer.objects.filter(business=business)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Customer retrieved")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Customer updated")
