from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *


class AccountSerializer(ModelSerializer):

    class Meta:
        model = Account
        fields = '__all__'


class TransactionSerializer(ModelSerializer):
    account = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = '__all__'

    def get_account(self, obj):
        return AccountSerializer(obj.get_account()).data


class CreditTransactionSerializer(ModelSerializer):
    transaction = TransactionSerializer(required=False)
    account = AccountSerializer(required=False)

    class Meta:
        model = CreditTransaction
        fields = '__all__'


class DebitTransactionSerializer(ModelSerializer):
    transaction = TransactionSerializer(required=False)
    account = AccountSerializer(required=False)

    class Meta:
        model = DebitTransaction
        fields = '__all__'
