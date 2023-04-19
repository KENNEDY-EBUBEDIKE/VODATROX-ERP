from rest_framework.serializers import ModelSerializer
from .models import *
from apps.users.serializers import UserSerializer


class SalesPersonSerializer(ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = SalesPerson
        fields = '__all__'


class SupplyTransactionSerializer(ModelSerializer):
    class Meta:
        model = SupplyTransaction
        fields = '__all__'


class DepositTransactionSerializer(ModelSerializer):
    sales_person = SalesPersonSerializer(required=False)

    class Meta:
        model = DepositTransaction
        fields = '__all__'


class DebtSerializer(ModelSerializer):
    debtor = UserSerializer(required=False)

    class Meta:
        model = Debt
        fields = '__all__'


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class StockInventorySerializer(ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = StockInventory
        fields = '__all__'


class PurchaseSerializer(ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Purchase
        fields = '__all__'
