"""New Transactions module"""
from .finance_transaction import DepositTransaction, SupplyTransaction
from .account_transaction import CreditTransaction, DebitTransaction


def finance_transaction_factory(api):
    """This is Implementation a factory that creates appropriate objects based on the `api` argument.
    When `api` is unknown, throw NotImplementedError exception."""

    # @TODO: Implementation

    if api == "deposit":
        provider = DepositTransaction()
    elif api == "supply":
        provider = SupplyTransaction()
    else:
        raise NotImplementedError
    return provider


def account_transaction_factory(api):
    """This is Implementation a factory that creates appropriate objects based on the `api` argument.
    When `api` is unknown, throw NotImplementedError exception."""

    # @TODO: Implementation

    if api == "credit":
        provider = CreditTransaction()
    elif api == "debit":
        provider = DebitTransaction()
    else:
        raise NotImplementedError
    return provider
