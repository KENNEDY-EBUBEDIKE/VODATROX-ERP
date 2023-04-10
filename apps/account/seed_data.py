from .models import Account


def seed_data(sender, **kwargs):
    # Create some records for MyModel
    try:
        Account.objects.create(
            account_name='VODATROX LTD',
            bank_name='STANBIC IBTC BANK',
            type='BANK',
            account_balance=0,

        )
        Account.objects.create(
            account_name='VODATROX LTD',
            bank_name='PROVIDUS BANK',
            type='BANK',
            account_balance=0,

        )

        Account.objects.create(
            account_name='VODATROX LTD',
            bank_name='VODATROX LTD CASH ACCOUNT',
            type='CASH',
            account_balance=0,
        )
    except Exception as e:
        print(e)
        pass
