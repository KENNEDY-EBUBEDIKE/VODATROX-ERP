from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from apps.users.models import User
from django.contrib.auth.models import Group
from apps.users.serializers import UserSerializer, MyAuthTokenSerializer
from rest_framework import status


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def users_list(request: Request) -> Response:
    print(request.user)
    users = User.objects.all()
    return Response({
        'success': True,
        'users': UserSerializer(users, many=True).data
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def register(request: Request) -> Response:
    if request.method == "PATCH":
        user_serializer = UserSerializer(instance=request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(
                data={
                    "success": True,
                    "user": user_serializer.data
                },
                status=status.HTTP_200_OK)


@api_view(["POST"])
def login(request: Request) -> Response:
    serializer = MyAuthTokenSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        # print(UserSerializer(user).data['groups'])
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
