"""
Views for wallets — list, retrieve, and create wallets.
Balance updates are handled via the ledger service, not here.
"""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.wallets.models import Wallet
from apps.wallets.serializers import WalletSerializer
from common.utilities.responses import success_response


class WalletListCreateView(generics.ListCreateAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(business__owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Wallets retrieved")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet = serializer.save()
        data = WalletSerializer(wallet).data
        return success_response(data=data, message="Wallet created", status=201)


class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        return Wallet.objects.filter(business__owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Wallet retrieved")
