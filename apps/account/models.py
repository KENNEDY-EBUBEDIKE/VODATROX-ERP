from django.db import models


class Account(models.Model):
    account_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    account_balance = models.BigIntegerField()

    class Meta:
        unique_together = (('account_name', 'bank_name'),)

    def transact(self,
                 initiator=None,
                 trx_type=None,
                 amount=None,
                 ref=None,
                 details=None,
                 trx_date=None,
                 source=None
                 ):
        #  generate Trx
        if trx_type == "DEBIT":
            ba = self.account_balance - amount
            md = DebitTransaction
        elif trx_type == "CREDIT":
            ba = self.account_balance + amount
            md = CreditTransaction
        else:
            return None
        trx = Transaction.objects.create(
            initiator=initiator,
            amount=amount,
            balance_before=self.account_balance,
            balance_after=ba,
            transaction_type=trx_type,
            transaction_details=details,
            transaction_reference=ref,
            transaction_date=trx_date,
            source=source,
        )

        obj = md.objects.create(
            transaction=trx,
            account=self
        )
        self.account_balance = ba
        self.save()

        return obj

    def __str__(self):
        return self.bank_name


class Transaction(models.Model):
    initiator = models.CharField(null=False, blank=False, max_length=255)
    amount = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    balance_before = models.BigIntegerField(null=True)
    balance_after = models.BigIntegerField(null=True)
    source = models.CharField(null=False, max_length=255)
    transaction_type = models.CharField(max_length=50, null=True)
    transaction_details = models.CharField(null=True, blank=True, max_length=255)
    transaction_reference = models.CharField(max_length=255)
    transaction_date = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.initiator

    def get_account(self):

        if self.transaction_type == "CREDIT":
            return self.credit.account

        elif self.transaction_type == "DEBIT":
            return self.debit.account


class CreditTransaction(models.Model):
    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE, related_name='credit', null=True)
    account = models.ForeignKey('Account', on_delete=models.DO_NOTHING, related_name='credit_transactions')

    def __str__(self):
        return self.initiator


class DebitTransaction(models.Model):
    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE, related_name='debit', null=True)
    account = models.ForeignKey('Account', on_delete=models.DO_NOTHING, related_name='debit_transactions')

    def __str__(self):
        return self.initiator
