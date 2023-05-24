from django import test
import faker
import models


class SalesPersonModelTestCase(TestCase):

    def __init__(self):
        self.fake = faker.Faker()

    def test_sales_person_creation(self):
        name = f'{self.fake.first_name()} {self.fake.password()}'

        code = self.fake.password(length=5, special_chars=False, digits=True, upper_case=True, lower_case=True)

        sales_person = models.objects.create(
            name=name,
            code=code,
        )

        self.assertTrue(isinstance(sales_person, SalesPerson))
        self.assertEqual(sales_person.name, name)
        self.assertEqual(sales_person.codee, code)

