from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from apps.account.models import Account
from apps.account.serializers import *


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def account(request: Request) -> Response:
    all_accounts = Account.objects.all()
    return Response({
        'success': True,
        "accounts": AccountSerializer(all_accounts, many=True).data,
    })
