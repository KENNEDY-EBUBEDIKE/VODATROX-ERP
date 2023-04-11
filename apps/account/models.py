from django.db import models


class Account(models.Model):
    account_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    account_balance = models.BigIntegerField()

    class Meta:
        unique_together = (('account_name', 'bank_name'),)

    def __str__(self):
        return self.bank_name


class Transaction(models.Model):
    initiator = models.CharField(null=False, blank=False, max_length=255)
    amount = models.DecimalField(null=False, max_digits=10, decimal_places=2)
    balance_before = models.BigIntegerField(null=True)
    balance_after = models.BigIntegerField(null=True)
    transaction_reference = models.CharField(max_length=255)
    transaction_date = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.initiator


class CreditTransaction(models.Model):
    CREDIT_CHOICES = (
        ("SALES", "SALES"),
    )

    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE, related_name='credit', null=True)
    credit_source = models.CharField(null=False, max_length=255, choices=CREDIT_CHOICES)
    account = models.ForeignKey('Account', on_delete=models.DO_NOTHING, related_name='credit_transactions')

    def __str__(self):
        return self.initiator


class DebitTransaction(models.Model):
    DEBIT_CHOICES = (
        ("BANK CHARGES", "BANK CHARGES"),
        ("PURCHASE ORDER", "PURCHASE ORDER"),
        ("STORAGE SPACE", "STORAGE SPACE"),
        ("OFF LOADING", "OFF LOADING"),
        ("CONVEYANCE", "CONVEYANCE"),
        ("MISCELLANEOUS", "MISCELLANEOUS"),
    )

    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE, related_name='debit', null=True)
    debit_source = models.CharField(null=False, max_length=255, choices=DEBIT_CHOICES)
    account = models.ForeignKey('Account', on_delete=models.DO_NOTHING, related_name='debit_transactions')

    def __str__(self):
        return self.initiator
