from rest_framework.serializers import ModelSerializer
from .models import *


class DepositSerializer(ModelSerializer):
    class Meta:
        model = Deposit
        fields = '__all__'

    def create(self, validated_data):
        deposit = Deposit()
        deposit.depositor = validated_data.get('depositor', deposit.depositor)
        deposit.amount = validated_data.get('amount', deposit.amount)
        deposit.date_of_payment = validated_data.get('date_of_payment', deposit.date_of_payment)

        deposit.save()
        return deposit


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        product = Product()
        product.name = validated_data.get('name', product.name).upper()
        product.alias_name = validated_data.get('alias_name', product.alias_name).upper()
        product.cost_price = validated_data.get('cost_price', product.cost_price)
        product.selling_price = validated_data.get('selling_price', product.selling_price)
        product.save()

        new_inventory = StockInventory()
        new_inventory.product = product
        new_inventory.stock_balance = 0
        new_inventory.save()
        return product


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


class SupplySerializer(ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Supply
        fields = '__all__'


class DebtSerializer(ModelSerializer):
    class Meta:
        model = Debt
        fields = '__all__'
