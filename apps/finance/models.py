from django.db import models
from datetime import datetime
from pytz import timezone


class SalesPerson(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='sales_person')
    account_balance = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def get_debt(self):
        try:
            return self.user.debt.amount
        except Exception as e:
            print(e)
            return 0

    def set_debt(self, amount):
        try:
            self.user.debt.amount = amount
            self.user.debt.save()
            return True
        except Exception as e:
            print(e)
            return 0


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("DEPOSIT", "Deposit"),
        ("SUPPLY", "Supply")
    )
    sales_person = models.ForeignKey('SalesPerson', on_delete=models.DO_NOTHING, null=True)
    amount = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    balance_before = models.BigIntegerField(default=0)
    balance_after = models.BigIntegerField(default=0)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES, null=True)
    transaction_date = models.DateTimeField(null=False)
    transaction_reference = models.CharField(null=True, blank=True, max_length=255)
    transaction_details = models.CharField(null=True, blank=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.sales_person)


class SupplyTransaction(models.Model):
    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE, related_name='supply')
    inventory_log = models.OneToOneField('InventoryLog', on_delete=models.SET_NULL, null=True, related_name='supply')
    product = models.ForeignKey('Product', on_delete=models.DO_NOTHING, related_name='supplies')
    quantity = models.IntegerField(null=True)

    def __str__(self):
        return self.transaction.sales_person


class DepositTransaction(models.Model):
    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE, related_name='deposit')
    credit = models.OneToOneField("account.CreditTransaction", on_delete=models.SET_NULL, null=True, related_name="deposit")
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.transaction.sales_person


class InventoryLog(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='inventory_log')
    details = models.CharField(max_length=1000, null=True, blank=True)
    previous_stock_balance = models.IntegerField(null=True, default=0)
    current_stock_balance = models.IntegerField(null=True, default=0)
    log_type = models.CharField(max_length=500, null=False, blank=False, choices=(("INC", "INC"), ("DEC", "DEC")))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('product', )

    def __str__(self):
        return self.product


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    alias_name = models.CharField(max_length=50)
    cost_price = models.IntegerField(null=True)
    selling_price = models.IntegerField(null=True)
    stock_balance = models.IntegerField(null=True, default=0)

    def change_stock_balance(self, quantity, direction, details):
        if direction == "DEC":
            bal = self.stock_balance - quantity
        elif direction == "INC":
            bal = self.stock_balance + quantity
        else:
            return None
        # create Log
        log = InventoryLog.objects.create(
            product=self,
            details=details,
            log_type=direction,
            previous_stock_balance=self.stock_balance,
            current_stock_balance=bal,
        )

        # change Balance
        self.stock_balance = log.current_stock_balance
        self.save()

        return log

    def __str__(self):
        return self.name


class Purchase(models.Model):
    product = models.ForeignKey('Product', null=True, on_delete=models.DO_NOTHING, related_name='purchases')
    debit = models.OneToOneField('account.DebitTransaction', null=True, on_delete=models.SET_NULL, related_name='purchase')
    log = models.OneToOneField('InventoryLog', null=True, on_delete=models.SET_NULL, related_name='purchase')
    quantity = models.IntegerField(null=False, blank=False, default=0)
    amount = models.IntegerField(null=False, blank=False, default=0)
    order_reference = models.CharField(max_length=100, blank=True, null=True)
    invoice_reference = models.CharField(max_length=100, blank=True, null=True)
    purchase_date = models.DateField(auto_now=False)
    is_delivered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product


class Debt(models.Model):
    debtor = models.OneToOneField('users.User', on_delete=models.DO_NOTHING, related_name="debt")
    amount = models.IntegerField(null=False, blank=False, default=0)
