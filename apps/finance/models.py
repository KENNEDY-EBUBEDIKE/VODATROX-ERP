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
    is_paid = models.BooleanField(default=False)
    product = models.ForeignKey('Product', on_delete=models.DO_NOTHING, related_name='supplies')
    quantity = models.IntegerField(null=True)

    def update_inventory(self, is_delete=False):
        if is_delete:
            self.product.inventory.stock_balance += self.quantity
            self.product.inventory.save()
        else:
            self.product.inventory.stock_balance -= self.quantity
            self.product.inventory.save()

    def __str__(self):
        return self.sales_person


class DepositTransaction(models.Model):
    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE, related_name='deposit')
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.sales_person


class StockInventory(models.Model):
    product = models.OneToOneField('Product', on_delete=models.CASCADE, related_name='inventory')
    stock_balance = models.IntegerField(null=True)

    class Meta:
        ordering = ('stock_balance', )

    def __str__(self):
        return self.product


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    alias_name = models.CharField(max_length=50)
    cost_price = models.IntegerField(null=True)
    selling_price = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    product = models.ForeignKey('Product', null=True, on_delete=models.DO_NOTHING, related_name='purchases')
    quantity = models.IntegerField(null=False, blank=False, default=0)
    reference = models.CharField(max_length=100, blank=True, null=True)
    purchase_date = models.DateField(auto_now=False)
    created_at = models.DateTimeField(auto_now=True)

    def update_inventory(self, delete=False):
        if delete:
            self.product.inventory.stock_balance -= self.quantity
            self.product.inventory.save()
        else:
            self.product.inventory.stock_balance += self.quantity
            self.product.inventory.save()

    def __str__(self):
        return self.product


class Debt(models.Model):
    debtor = models.OneToOneField('users.User', on_delete=models.DO_NOTHING, related_name="debt")
    amount = models.IntegerField(null=False, blank=False, default=0)
