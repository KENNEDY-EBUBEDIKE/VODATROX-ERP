from django.db import models


class StockInventory(models.Model):
    product = models.OneToOneField('Product', on_delete=models.CASCADE, related_name='inventory')
    stock_balance = models.IntegerField(null=True)

    def __str__(self):
        return self.product


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    alias_name = models.CharField(max_length=50)
    cost_price = models.IntegerField(null=True)
    selling_price = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class Deposit (models.Model):
    depositor = models.CharField(max_length=255, null=True, blank=True)
    amount = models.IntegerField(null=False)
    is_confirmed = models.BooleanField(default=False)
    date_of_payment = models.DateField(auto_now=False)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.depositor} => {self.amount}'


class Supply(models.Model):
    sales_person = models.CharField(max_length=255)
    product = models.ForeignKey('Product', on_delete=models.DO_NOTHING, related_name='supplies')
    quantity = models.IntegerField(null=True)
    date_supplied = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now=True)

    def update_inventory(self, is_delete=False):
        if is_delete:
            self.product.inventory.stock_balance += self.quantity
            self.product.inventory.save()
        else:
            self.product.inventory.stock_balance -= self.quantity
            self.product.inventory.save()

    def __str__(self):
        return self.sales_person


class Purchase(models.Model):
    product = models.ForeignKey('Product', null=True, on_delete=models.DO_NOTHING, related_name='purchases')
    quantity = models.IntegerField(null=False, blank=False, default=0)
    reference = models.CharField(max_length=100, blank=True, null=True)
    purchase_date = models.DateField(auto_now=True)
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
