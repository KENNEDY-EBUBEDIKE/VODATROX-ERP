from .base_transaction import BaseTransaction
from . import errors
from apps.finance.models import Debt


class DepositTransaction(BaseTransaction):
    """ Deposit Transaction processor """

    deposit = None
    debt = None

    def _prepare_transaction(self):
        """Arrange and validate the necessary data for the transaction"""
        pass

    def _process_debt(self):
        """Process the sales person's Debt"""
        sales_person_debt = Debt.objects.get_or_create(debtor=self.deposit.sales_person.user)
        self.debt = sales_person_debt[0].amount - self.deposit.amount
        try:
            assert abs(self.new_balance) == abs(self.debt), "Not Balanced"
        except AssertionError:
            raise errors.AccountNotBalanced("Debt and Account Balance is not in sync")

    def set_balances(self, deposit):
        """Set balances
        Make the method chainable"""
        # @TODO: Implement it

        self.deposit = deposit
        self.amount = deposit.amount
        self.balance_before = deposit.sales_person.account_balance
        self.balance_after = deposit.amount + self.balance_before
        self.new_balance = self.balance_after
        self._process_debt()
        return True, self

    def initiate(self, *args, **kwargs):
        """Finalise the transaction"""
        deposit = kwargs['deposit']
        deposit.transaction_reference = self.reference
        deposit.balance_before = self.balance_before
        deposit.balance_after = self.balance_after
        deposit.transaction_type = "DEPOSIT"
        deposit.sales_person.account_balance = self.new_balance

        debt = Debt.objects.get_or_create(debtor=self.deposit.sales_person.user)[0]
        debt.amount = self.debt
        deposit.is_confirmed = True
        self.deposit.save()
        debt.save()
        return True


class SupplyTransaction(BaseTransaction):
    """ Supply Transaction processor """
