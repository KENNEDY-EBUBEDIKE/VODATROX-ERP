from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from apps.users.models import User
from apps.users.serializers import UserSerializer, MyAuthTokenSerializer
import time


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def users_list(request: Request) -> Response:
    print(request.user)
    users = User.objects.all()
    return Response({
        'success': True,
        'users': UserSerializer(users, many=True).data
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register(request: Request) -> Response:
    print(request.data)
    return Response({
        'success': True,
        'users': UserSerializer(users, many=True).data
    })


@api_view(["POST"])
def login(request: Request) -> Response:
    time.sleep(3)
    serializer = MyAuthTokenSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'success': True,
            'token': token.key,
            'user': UserSerializer(user).data
        })
    else:
        return Response({
            'success': False,
            'error': serializer.errors
        })
