from .base_transaction import BaseTransaction
from . import errors
from apps.account.models import Account
from apps.account.models import CreditTransaction as CT


class CreditTransaction(BaseTransaction):
    """ Deposit Transaction processor """

    source = None

    def _prepare_transaction(self, *args, **kwargs):
        """Arrange and validate the necessary data for the transaction"""
        self.amount = kwargs['deposit_transaction'].deposit.amount
        self.reference = kwargs['deposit_transaction'].reference
        self.source = kwargs['source']

    def set_balances(self, deposit_transaction, account):
        """Set balances
        Make the method chainable"""
        # @TODO: Implement it

        self.balance_before = account.account_balance
        self.balance_after = deposit_transaction.deposit.amount + self.balance_before
        self.new_balance = self.balance_after

        return True, self

    def initiate(self, *args, **kwargs):
        """Finalise the transaction"""

        self._prepare_transaction(
            deposit_transaction=kwargs['deposit_transaction'],
            account=kwargs['account'],
            source=kwargs['source']
        ),

        CT.objects.create(
            initiator=f"{kwargs['deposit_transaction'].deposit.sales_person.user.first_name} {kwargs['deposit_transaction'].deposit.sales_person.user.surname}",
            amount=self.amount,
            balance_before=self.balance_before,
            balance_after=self.balance_after,
            transaction_reference=self.reference,
            transaction_date=kwargs['deposit_transaction'].deposit.transaction_date,
            credit_source=self.source,
            account=kwargs['account']
        )

        kwargs['account'].account_balance = self.new_balance
        kwargs['account'].save()
        return True


class DebitTransaction(BaseTransaction):
    """ Supply Transaction processor """
