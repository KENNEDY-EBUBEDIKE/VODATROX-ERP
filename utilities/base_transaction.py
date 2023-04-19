import abc
from functools import wraps
from apps.finance.models import DepositTransaction
from apps.account.models import CreditTransaction
import utilities
from utilities import errors


class BaseTransaction(metaclass=abc.ABCMeta):
    """Base SMS Provider class"""

    reference = None
    balance_before = None
    balance_after = None
    new_balance = None
    amount = None

    # pylint: disable=no-self-argument
    # @staticmethod
    # def _validation(func):
    #     """Validation decorator"""
    #
    #     @wraps(func)
    #     def wrapped(obj, *args, **kwargs):
    #         # pylint: disable=no-member, not-callable
    #         if not isinstance(deposit, DepositTransaction):
    #             raise errors.WrongObject("Argument 'deposit' must be an instance of DepositTransaction class")
    #         return func(obj, *args, **kwargs)
    #     return wrapped

    @abc.abstractmethod
    def _prepare_transaction(self, *args, **kwargs):
        """Protected abstract method responsible for Preparing Transaction"""
        pass

    @abc.abstractmethod
    def initiate(self):
        """Abstract transaction initiation method"""
        pass

    def set_transaction_reference(self, reference):
        """Set reference and make the method chainable"""

        if isinstance(self, utilities.finance_transaction.DepositTransaction):
            if DepositTransaction.objects.filter(transaction__transaction_reference=reference).exists():
                raise errors.DuplicateTransactionReference("A Transaction Already has this Reference")
            else:
                self.reference = reference
        elif isinstance(self, utilities.account_transaction.CreditTransaction):
            if CreditTransaction.objects.filter(transaction__transaction_reference=reference).exists():
                raise errors.DuplicateTransactionReference("A Transaction Already has this Reference")
            else:
                self.reference = reference
        return self
