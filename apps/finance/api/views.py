from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from apps.finance.models import *
from rest_framework import status
from apps.finance.serializers import *
from apps.users.serializers import *
from utilities import account_transaction_factory, finance_transaction_factory
import datetime
from django.conf import settings
import pytz
from apps.account.models import Account
from django.db.models import F, Value, CharField, Sum


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sales_persons(request: Request) -> Response:
    if request.method == "GET":

        if request.GET.get('id', None):
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
        purchase_serializer = PurchaseSerializer(data=request.data)
        if purchase_serializer.is_valid():
            product = Product.objects.get(id=request.data.get('product'))
            account = Account.objects.get(id=request.data.get('account'))
            quantity = int(request.data.get('quantity'))
            amount = product.cost_price * quantity

            # Debit the biz account
            debit = account.transact(
                initiator=f"{request.user.first_name} {request.user.surname}",
                trx_type="DEBIT",
                amount=amount,
                details=f"Purchase of {quantity} cartons of {product.name}",
                ref=f"PUR/{request.data.get('order_reference')}",
                trx_date=request.data.get('purchase_date'),
                source="PURCHASE ORDER",
            )
            if debit:
                purchase_serializer.save(
                    product=product,
                    debit=debit,
                    amount=amount,
                    expected_revenue=(quantity * product.selling_price)
                )

        else:
            return Response(
                data={"success": False,
                      "message": purchase_serializer.errors
                      },
                status=status.HTTP_200_OK
            )
        return Response({
            'success': True,
            'message': "Order Placed Successfully",

        }, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        p = Purchase.objects.get(id=request.GET['id'])
        if not p.is_delivered:
            p.debit.account.transact(
                initiator=f"{request.user.first_name} {request.user.surname}",
                trx_type="CREDIT",
                amount=p.amount,
                details=f"Reversal of purchase error",
                ref=f"REVERSAL/{p.order_reference}",
                trx_date=datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE)),
                source="REVERSAL",
            )
            p.delete()
            return Response({
                'success': True,
            }, status=status.HTTP_200_OK)

    purchases = Purchase.objects.all().order_by('-quantity', 'purchase_date')
    return Response({
        'success': True,
        'purchases': PurchaseSerializer(purchases, many=True).data
    })


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def confirm_purchase_delivery(request: Request) -> Response:
    if request.method == "PATCH":
        p = Purchase.objects.get(id=request.data['id'])
        p.invoice_reference = request.data.get('invoice_reference')
        log = p.product.change_stock_balance(
            p.quantity,
            direction="INC",
            details=f"PURCHASE OF {p.quantity} CARTONS OF {p.product.name}",
        )
        p.is_delivered = True
        p.delivery_date = datetime.datetime.now(tz=pytz.timezone("Africa/Lagos"))
        p.log = log
        p.save()
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def supply(request: Request) -> Response:
    if request.method == "POST":
        sales_person = SalesPerson.objects.get(id=int(request.data.get('sales_person')))
        product = Product.objects.get(id=int(request.data.get('product')))
        quantity = int(request.data.get('quantity'))
        date_supplied = request.data.get('date_supplied')
        reference = f"SP/{int(datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE)).timestamp())}"
        if request.data.get('rate', None):
            rate = int(request.data['rate'])
        else:
            rate = product.selling_price
        amount = int(quantity * rate)
        bb = sales_person.account_balance
        ba = bb - amount

        try:
            assert abs(ba) == abs((sales_person.get_debt() + amount)), "Balance Inconsistency"

            transaction = Transaction.objects.create(
                sales_person=sales_person,
                amount=amount,
                balance_before=bb,
                balance_after=ba,
                transaction_type="SUPPLY",
                transaction_date=date_supplied,
                transaction_reference=reference,
                transaction_details=f"{quantity} CARTONS OF {product.name}"
            )

            log = product.change_stock_balance(
                quantity,
                direction="DEC",
                details=f"{quantity} CARTONS OF {product.name}",
            )

            SupplyTransaction.objects.create(
                transaction=transaction,
                quantity=quantity,
                product=product,
                inventory_log=log,
            )

            sales_person.account_balance = ba
            sales_person.set_debt(sales_person.get_debt() + amount)
            sales_person.save()

            return Response({
                'success': True,
                'message': "Supplied Successfully",
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': e.args[0],
            }, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        sp = SupplyTransaction.objects.get(id=request.GET['id'])

        # Increase Stock
        sp.product.change_stock_balance(
            sp.quantity,
            direction="INC",
            details=f"REVERSAL FOR {sp.quantity} CTNS OF {sp.product.name}",
        )

        # Reduce Debt
        sp.transaction.sales_person.set_debt(sp.transaction.sales_person.get_debt() - sp.transaction.amount)

        # Increase Sales Person's Account Bal
        sp.transaction.sales_person.account_balance = sp.transaction.sales_person.account_balance + sp.transaction.amount
        sp.transaction.sales_person.save()

        sp.transaction.delete()

        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)

    supplies = SupplyTransaction.objects.all().order_by('transaction__transaction_date', 'quantity')
    return Response({
        'success': True,
        'supplies': SupplyTransactionSerializer(supplies, many=True).data
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
            products = Product.objects.all().order_by('-stock_balance')

            # annotate adds a new field 'stock_value' to the Qs.
            # aggregate works on a particular field in a Qs (in this case, sum operation) and
            # returns a dict as the result of the operation.
            total_stock_value = products.annotate(
                stock_value=F('cost_price') * F('stock_balance')).aggregate(Sum('stock_value'))['stock_value__sum']

            return Response({
                'success': True,
                'products': ProductSerializer(products, many=True).data,
                'total_stock_balance': products.aggregate(Sum('stock_balance'))['stock_balance__sum'],
                'total_stock_value': total_stock_value
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

        try:
            trx = Transaction.objects.create(
                sales_person=SalesPerson.objects.get(id=int(request.data['sales_person'])),
                transaction_type="DEPOSIT",
                amount=request.data['amount'],
                transaction_date=request.data['transaction_date'],
                transaction_details=request.data['transaction_details'],
            )
            DepositTransaction.objects.create(
                transaction=trx
            )
        except Exception as e:
            return Response(
                data={"success": False,
                      "message": e.args[0]
                      },
                status=status.HTTP_200_OK
            )

        return Response({
            'success': True,
            'message': "Deposit Lodged Successfully. Kindly Wait for Confirmation"
        }, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        deposit = DepositTransaction.objects.get(id=request.GET['id'])
        if not deposit.is_confirmed:
            deposit.transaction.delete()
            return Response({
                'success': True,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': "You cannot Delete a Confirmed Deposit"
            }, status=status.HTTP_200_OK)

    elif request.method == "GET":
        all_deposits = DepositTransaction.objects.all().order_by(
            'transaction__transaction_date', 'is_confirmed',
            'transaction__amount')
        return Response({
            'success': True,
            "deposits": DepositTransactionSerializer(all_deposits, many=True).data,
        })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def debt(request: Request) -> Response:
    if request.method == "GET":
        all_debts = Debt.objects.all().order_by('amount')
        return Response({
            'success': True,
            "debts": DebtSerializer(all_debts, many=True).data,
            "total_debt": sum(all_debts.values_list('amount', flat=True)),
        })


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def confirm_deposit(request: Request) -> Response:
    if request.method == "POST":
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
                        if finance_transaction_module.initiate(deposit=deposit):
                            account_transaction_module.initiate(
                                deposit_transaction=deposit_transaction,
                                account=account,
                                source=credit_source
                            )

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
    elif request.method == "GET":
        deposit = DepositTransaction.objects.get(id=request.GET['id'])
        if deposit.is_confirmed:
            deposit.is_confirmed = False

            deposit.transaction.transaction_reference = None
            deposit.transaction.balance_before = 0
            deposit.transaction.balance_after = 0

            debt = Debt.objects.get(debtor=deposit.transaction.sales_person.user)
            debt.amount += deposit.transaction.amount

            deposit.transaction.sales_person.account_balance -= deposit.transaction.amount

            deposit.credit.account.account_balance -= deposit.transaction.amount

            deposit.transaction.sales_person.save()
            deposit.transaction.save()
            deposit.save()
            debt.save()
            deposit.credit.account.save()
            deposit.credit.transaction.delete()

            return Response({
                'success': True,
                'message': "Deposit Unconfirmed"
            })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transactions(request: Request) -> Response:
    sales_person = SalesPerson.objects.get(id=request.GET['sales_person_id'])

    # The annotate method adds extra field to the filtered Qs

    # deposit_transactions = DepositTransaction.objects.filter(sales_person=sales_person).annotate(
    #     transaction_kind=Value('Deposit', output_field=CharField())
    # )

    deposit_transactions = Transaction.objects.filter(
        sales_person=sales_person,
        deposit__is_confirmed=True,
        transaction_type="DEPOSIT"
    )
    supply_transactions = Transaction.objects.filter(
        sales_person=sales_person,
        transaction_type="SUPPLY"
    )

    # Then union joins the Qs
    all_sales_persons_transactions = deposit_transactions.union(supply_transactions).order_by('transaction_date')

    return Response({
        'success': True,
        'transactions': TransactionSerializer(all_sales_persons_transactions, many=True).data
    })
