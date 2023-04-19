from .models import User


def seed_data(sender, **kwargs):
    # Create some records for MyModel
    try:
        User.objects.create_superuser(
            email='admin@vodatrox.com',
            username='admin',
            password='admin001',
            first_name="KENNEDY",
            surname="EZIECHINA",
            phone_number="8034173780",
            appointment="ADMIN",

        )
    except Exception as e:
        print(e)
        pass
