from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from apps.account.models import Account, Transaction
from apps.account.serializers import *
from django.db.models import F, Value, CharField, Sum


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def account(request: Request) -> Response:
    if request.user.is_superuser:
        all_accounts = Account.objects.all()
        return Response({
            'success': True,
            "accounts": AccountSerializer(all_accounts, many=True).data,
            "total_balance": all_accounts.aggregate(Sum('account_balance'))['account_balance__sum'],
        })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def credit_account(request: Request) -> Response:
    if request.user.is_superuser:
        try:

            acct = Account.objects.get(id=request.data['account'])
            acct.transact(
                initiator=f"{request.user.first_name} {request.user.surname}",
                trx_type="CREDIT",
                amount=int(request.data['amount'], 10),
                details=request.data['transaction_details'],
                ref=request.data['transaction_reference'],
                trx_date=request.data['transaction_date'],
                source=request.data['source'],
            )
            return Response({
                'success': True,
                'message': "Account Credited Successfully",
            })
        except Exception as e:
            return Response({
                "success": False,
                "message": e.args[0]
            })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def debit_account(request: Request) -> Response:
    if request.user.is_superuser:
        acct = Account.objects.get(id=request.data['account'])
        acct.transact(
            initiator=f"{request.user.first_name} {request.user.surname}",
            trx_type="DEBIT",
            amount=int(request.data['amount']),
            details=request.data['transaction_details'],
            ref=request.data['transaction_reference'],
            trx_date=request.data['transaction_date'],
            source=request.data['source'],
        )
        return Response({
            'success': True,
            'message': "Account Debited Successfully",
        })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transactions(request: Request) -> Response:
    if request.user.is_superuser:
        all_transactions = Transaction.objects.all().order_by('-created_at')
        return Response({
            'success': True,
            'transactions': TransactionSerializer(all_transactions, many=True).data
        })
