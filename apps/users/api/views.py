from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from apps.users.models import User
from apps.finance.models import SalesPerson
from django.contrib.auth.models import Group
from apps.users.serializers import UserSerializer, MyAuthTokenSerializer
from apps.finance.models import Debt
from rest_framework import status


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def users_list(request: Request) -> Response:
    users = User.objects.all()
    return Response({
        'success': True,
        'users': UserSerializer(users, many=True).data
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request: Request) -> Response:
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
        user.update_last_login()
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


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_status(request: Request) -> Response:
    user = User.objects.get(id=request.data['id'])
    user.is_active = not user.is_active
    user.save()
    return Response({
        'success': True,
        'message': "Updated Successfully",
    })


@api_view(["GET", "DELETE", "POST"])
@permission_classes([IsAuthenticated])
def user(request: Request) -> Response:
    if request.method == "DELETE":
        User.objects.get(id=request.GET.get('id')).delete()
        return Response({
            'success': True,
            'message': "Deleted Successfully",
        })

    if request.method == "POST":
        try:
            new_user = User.objects.create_user(
                email=request.data['email'],
                username=request.data['surname'] + "-" + request.data['first_name'],
                password=request.data['surname'].lower() + "@001",
                first_name=request.data['first_name'],
                surname=request.data['surname'],
                phone_number=request.data['phone_number'],
                appointment=request.data['appointment'],

            )

            if request.data['appointment'] == "STAFF":
                new_user.is_staff = True

            if request.data['appointment'] == "SALES PERSON":
                SalesPerson.objects.create(user=new_user)

            if request.data['appointment'] == "ADMIN":
                new_user.is_staff = True
                new_user.is_superuser = True
            new_user.save()

            Debt.objects.create(debtor=new_user)
        except Exception as e:
            print(e)
            return Response({
                'success': False,
                'message': e.args[0],
            })
        return Response({
            'success': True,
            'message': "Account Created Successfully",
        })
    elif request.method == "GET":
        return Response({
            'success': True,
            'user': UserSerializer(User.objects.get(id=request.data['id'])).data
        })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def add_to_sales_persons(request):
    user = User.objects.get(id=request.data['id'])
    SalesPerson.objects.create(user=user)
    return Response({
        'success': True,
        'message': "Updated Successfully",
    })
