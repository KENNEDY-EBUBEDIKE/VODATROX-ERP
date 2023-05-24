class BaseError(Exception):
    """Base exception class"""


class IncompleteTransaction(BaseError):
    """Incomplete Transaction exception"""


class DuplicateTransactionReference(BaseError):
    """Duplicate Transaction Reference exception """


class WrongObject(BaseError):
    """Wrong Object Passed Exception"""


class AccountNotBalanced(BaseError):
    """Account Imbalance Exception"""
