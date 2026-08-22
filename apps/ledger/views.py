"""
Views for ledger — read-only (entries are created via LedgerService).
"""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.ledger.models import LedgerAccount, LedgerTransaction
from apps.ledger.serializers import LedgerAccountSerializer, LedgerTransactionSerializer
from common.utilities.responses import success_response


class LedgerAccountListView(generics.ListAPIView):
    serializer_class = LedgerAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LedgerAccount.objects.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Ledger accounts retrieved")


class LedgerTransactionListView(generics.ListAPIView):
    serializer_class = LedgerTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = LedgerTransaction.objects.all()
        reference = self.request.query_params.get("reference")
        if reference:
            queryset = queryset.filter(reference__icontains=reference)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Ledger transactions retrieved")


class LedgerTransactionDetailView(generics.RetrieveAPIView):
    serializer_class = LedgerTransactionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"
    queryset = LedgerTransaction.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Ledger transaction retrieved")
