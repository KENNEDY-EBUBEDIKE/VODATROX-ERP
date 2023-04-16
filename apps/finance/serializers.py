from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
from apps.users.serializers import UserSerializer


class SalesPersonSerializer(ModelSerializer):
    debt = serializers.SerializerMethodField()
    user = UserSerializer(required=False)

    class Meta:
        model = SalesPerson
        fields = '__all__'

    def get_debt(self, obj):
        return obj.get_debt()


class TransactionSerializer(ModelSerializer):
    sales_person = SalesPersonSerializer(required=False)

    class Meta:
        model = Transaction
        fields = '__all__'


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class SupplyTransactionSerializer(ModelSerializer):
    transaction = TransactionSerializer(required=False)
    product = ProductSerializer(required=False)

    class Meta:
        model = SupplyTransaction
        fields = '__all__'


class DepositTransactionSerializer(ModelSerializer):
    transaction = TransactionSerializer(required=False)

    class Meta:
        model = DepositTransaction
        fields = '__all__'


class DebtSerializer(ModelSerializer):
    debtor = UserSerializer(required=False)

    class Meta:
        model = Debt
        fields = '__all__'


class InventoryLogSerializer(ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = InventoryLog
        fields = '__all__'


class PurchaseSerializer(ModelSerializer):
    product = ProductSerializer(required=False)

    class Meta:
        model = Purchase
        fields = '__all__'
