from rest_framework.serializers import ModelSerializer
from .models import *


class AccountSerializer(ModelSerializer):

    class Meta:
        model = Account
        fields = '__all__'
