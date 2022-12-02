from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from apps.finance.models import Deposit, StockInventory, Product, Purchase, Supply, Debt
from rest_framework import status
from apps.finance.serializers import *


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


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def inventory(request: Request) -> Response:
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
        deposit = Product.objects.get(id=request.GET['id'])
        deposit.delete()
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)
    inventories = StockInventory.objects.all().order_by('-stock_balance')
    return Response({
        'success': True,
        'inventories': StockInventorySerializer(inventories, many=True).data
    })


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def deposits(request: Request) -> Response:
    if request.method == "POST":
        deposit_serializer = DepositSerializer(data=request.data)
        if deposit_serializer.is_valid():
            deposit_serializer.save()

            try:
                debtor = Debt.objects.get(name=deposit_serializer.data['depositor'])
                debtor.amount -= deposit_serializer.data['amount']
            except Exception as e:
                print(e)
                debtor = Debt()
                debtor.name = deposit_serializer.data['depositor']
                debtor.amount = -deposit_serializer.data['amount']

            debtor.save()

            return Response({
                'success': True,
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"success": False,
                      "error": deposit_serializer.errors},
                status=status.HTTP_200_OK
            )

    if request.method == "DELETE":
        deposit = Deposit.objects.get(id=request.GET['id'])
        deposit.delete()

        debtor = Debt.objects.get(name=deposit.depositor)
        debtor.amount += deposit.amount
        debtor.save()

        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)

    all_deposits = Deposit.objects.all().order_by('date_of_payment', 'is_confirmed', 'amount')
    return Response({
        'success': True,
        "deposits": DepositSerializer(all_deposits, many=True).data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def debt(request: Request) -> Response:
    all_debts = Debt.objects.all().order_by('amount')
    return Response({
        'success': True,
        "debts": DebtSerializer(all_debts, many=True).data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def confirm_deposit(request: Request) -> Response:
    deposit = Deposit.objects.get(id=request.GET['id'])
    deposit.is_confirmed = True
    deposit.save()
    return Response({
        'success': True,
    })
