from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
# from apps.users.models import User
# from apps.users.serializers import U
import time


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def inventory(request: Request) -> Response:
    return Response({
        'success': True
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def account_receivables(request: Request) -> Response:
    return Response({
        'success': True
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def payments(request: Request) -> Response:
    return Response({
        'success': True
    })
