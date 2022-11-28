from django.db import models


class Payment(models.Model):
    depositor = models.CharField(max_length=255, null=True, blank=True)
    amount = models.IntegerField(null=False)
    is_confirmed = models.BooleanField(default=False)
    date_of_payment = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.depositor} =< {self.amount}'
