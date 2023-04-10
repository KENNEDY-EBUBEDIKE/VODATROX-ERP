from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from apps.finance.models import *
from rest_framework import status
from apps.finance.serializers import *
from apps.users.serializers import *
from utilities import account_transaction_factory, finance_transaction_factory
from apps.account.models import Account
from django.db.models import F, Value, CharField
from itertools import chain
import json


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sales_persons(request: Request) -> Response:
    if request.method == "GET":

        if request.GET['id']:
            try:
                sales_person = SalesPerson.objects.get(user__id=request.GET['id'])
                return Response({
                    'success': True,
                    'sales_person': SalesPersonSerializer(sales_person).data
                })
            except Exception as e:
                print(e)
                return Response({
                    'success': False,
                    'message': "This User is not a Sales Person",
                })
        else:

            all_sales_persons = SalesPerson.objects.all()
            return Response({
                'success': True,
                'sales_persons': SalesPersonSerializer(all_sales_persons, many=True).data
            })


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def purchase(request: Request) -> Response:
    if request.method == "POST":
        pc = Purchase()
        pc.product = Product.objects.get(id=request.data.get('product'))
        pc.quantity = int(request.data.get('quantity'))
        pc.purchase_date = request.data.get('purchase_date')
        pc.reference = request.data.get('reference')
        pc.save()
        pc.update_inventory()
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        p = Purchase.objects.get(id=request.GET['id'])
        p.delete()
        p.update_inventory(delete=True)
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)

    purchases = Purchase.objects.all().order_by('-quantity', 'purchase_date')
    return Response({
        'success': True,
        'purchases': PurchaseSerializer(purchases, many=True).data
    })


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def supply(request: Request) -> Response:
    if request.method == "POST":
        sp = Supply()
        sp.sales_person = request.data.get('sales_person')
        sp.product = Product.objects.get(id=request.data.get('product'))
        sp.quantity = int(request.data.get('quantity'))
        sp.date_supplied = request.data.get('date_supplied')

        sp.save()
        sp.update_inventory()

        try:
            debtor = Debt.objects.get(name=sp.sales_person)
            debtor.amount += (sp.product.selling_price * sp.quantity)
        except Exception as e:
            print(e)
            debtor = Debt()
            debtor.name = sp.sales_person
            debtor.amount = (sp.product.selling_price * sp.quantity)
        debtor.save()
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        sp = Supply.objects.get(id=request.GET['id'])
        sp.delete()
        sp.update_inventory(is_delete=True)
        debtor = Debt.objects.get(name=sp.sales_person)
        debtor.amount -= (sp.product.selling_price * sp.quantity)
        debtor.save()
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)

    supplies = Supply.objects.all().order_by('date_supplied', 'quantity')
    return Response({
        'success': True,
        'supplies': SupplySerializer(supplies, many=True).data
    })


@api_view(["GET", "POST", "DELETE", "PATCH"])
@permission_classes([IsAuthenticated])
def inventory(request: Request) -> Response:

    if request.method == "GET":
        pk = request.GET.get('id')
        if pk:
            product = Product.objects.get(id=pk)
            return Response({
                'success': True,
                'product': ProductSerializer(product).data
            }, status=status.HTTP_200_OK)
        else:
            inventories = StockInventory.objects.all().order_by('-stock_balance')
            return Response({
                'success': True,
                'inventories': StockInventorySerializer(inventories, many=True).data
            })
    if request.method == "POST":
        product_serializer = ProductSerializer(data=request.data)
        if product_serializer.is_valid():
            product_serializer.save()

            return Response({
                'success': True,
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"success": False,
                      "error": product_serializer.errors},
                status=status.HTTP_200_OK
            )
    if request.method == "DELETE":
        product = Product.objects.get(id=request.GET['id'])
        product.delete()
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)

    if request.method == "PATCH":
        print(request.data)
        product = Product.objects.get(id=request.data.get("pk"))
        product_serializer = ProductSerializer(instance=product, data=request.data, partial=True)
        if product_serializer.is_valid():
            product_serializer.save()
        else:
            print(product_serializer.errors)
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def deposits(request: Request) -> Response:

    if request.method == "POST":
        deposit_serializer = DepositTransactionSerializer(data=request.data)
        if deposit_serializer.is_valid():
            deposit_serializer.save(
                transaction_type="DEPOSIT",
                sales_person=SalesPerson.objects.get(id=int(request.data['sales_person']))
            )

            return Response({
                'success': True,
                'message': "Deposit Lodged Successfully. Kindly Wait for Confirmation"
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"success": False,
                      "message": deposit_serializer.errors
                      },
                status=status.HTTP_200_OK
            )

    elif request.method == "DELETE":
        deposit = DepositTransaction.objects.get(id=request.GET['id'])
        if not deposit.is_confirmed:
            deposit.delete()
            return Response({
                'success': True,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': "You cannot Delete a Confirmed Deposit"
            }, status=status.HTTP_200_OK)

    elif request.method == "GET":
        all_deposits = DepositTransaction.objects.all().order_by('transaction_date', 'is_confirmed', 'amount')
        return Response({
            'success': True,
            "deposits": DepositTransactionSerializer(all_deposits, many=True).data,
        })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def debt(request: Request) -> Response:
    all_debts = Debt.objects.all().order_by('amount')
    return Response({
        'success': True,
        "debts": DebtSerializer(all_debts, many=True).data,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm_deposit(request: Request) -> Response:
    deposit = DepositTransaction.objects.get(id=request.data['id'])
    account = Account.objects.get(id=request.data['account'])
    credit_source = request.data['source']
    if not deposit.is_confirmed:
        try:
            # @TODO: process the Deposit to affect the sales person's account

            finance_transaction_module = finance_transaction_factory("deposit")
            deposit_completed, deposit_transaction = (
                finance_transaction_module
                .set_transaction_reference(request.data['reference'])
                .set_balances(deposit)
            )
            if deposit_completed:

                # @TODO: process the Deposit to affect the Cashbook account
                account_transaction_module = account_transaction_factory("credit")
                credit_completed, credit_transaction = (
                    account_transaction_module
                    .set_transaction_reference(request.data['reference'])
                    .set_balances(deposit_transaction, account)
                )

                if credit_completed:
                    finance_transaction_module.initiate(deposit=deposit)
                    account_transaction_module.initiate(deposit_transaction=deposit_transaction, account=account, source=credit_source)
                    return Response({
                        'success': True,
                        'message': "Deposit Confirmed"
                    })
        except Exception as e:
            print(e)
            return Response({
                'success': False,
                'message': e.args[0]
            })
    # elif deposit.is_confirmed:
    #     deposit.is_confirmed = False
    #     debtor = Debt.objects.get(debtor=deposit.sales_person)
    #     debtor.amount += deposit.amount
    #     debtor.save()
    #     deposit.save()
    #
    #     return Response({
    #         'success': True,
    #         'message': "Deposit Unconfirmed"
    #     })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transactions(request: Request) -> Response:
    sales_person = SalesPerson.objects.get(id=request.GET['sales_person_id'])

    # The annotate method adds extra field to the filtered Qs
    # Then union joins the Qs
    # deposit_transactions = DepositTransaction.objects.filter(sales_person=sales_person).annotate(
    #     transaction_kind=Value('Deposit', output_field=CharField())
    # )
    # supply_transactions = SupplyTransaction.objects.filter(sales_person=sales_person).annotate(
    #     transaction_kind=Value('Supply', output_field=CharField())
    # )
    # all_sales_persons_transactions = deposit_transactions.union(supply_transactions).order_by('transaction_date')

    results = Transaction.objects.filter(sales_person=sales_person).select_subclasses()
    print(results)

    return Response({
        'success': True,
        # 'transactions': all_sales_persons_transactions
    })
