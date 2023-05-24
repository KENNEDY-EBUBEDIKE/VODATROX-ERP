from django.urls import path
from django.conf import settings
from .views import *

urlpatterns = [
    path('accounts/', account, name='api-account'),
    path('credit-account/', credit_account, name='api-credit_account'),
    path('debit-account/', debit_account, name='api-debit_account'),
    path('inter-transfer/', inter_account_transfer, name='api-inter_account_transfer'),
    path('transactions/', transactions, name='api-transactions'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
