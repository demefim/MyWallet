from rest_framework import views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from MyWallet.models import Account, Category, Split, Transaction
from MyWallet.rest import serializers
from MyWallet.rest.permissions import ProtectSystemAccount
from MyWallet.rest.serializers import (AccountSerializer, CategorySerializer, SplitSerializer, TransactionSerializer)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (ProtectSystemAccount,)

    @action(detail=True)
    def transactions(self, request, pk=None):
        account = self.get_object()
        transactions = Split.objects.filter(account=account)
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = SplitSerializer(page, many=True, context={'request': request})
            return Response(serializer.data)
        serializer = SplitSerializer(transactions, many=True, context={'request': request})
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class AccountNameView(views.APIView):
    def get(self, request, format=None):
        serializer = serializers.AccountNameSerializer(Account.objects.all(), many=True)
        return Response(serializer.data)


class PersonalAccountsView(views.APIView):
    def get(self, request, format=None):
        serializer = serializers.AccountSerializer(
            Account.objects.filter(account_type=Account.PERSONAL), many=True)
        return Response(serializer.data)


class ForeignAccountsView(views.APIView):
    def get(self, request, format=None):
        serializer = serializers.AccountSerializer(
            Account.objects.filter(account_type=Account.FOREIGN), many=True)
        return Response(serializer.data)
