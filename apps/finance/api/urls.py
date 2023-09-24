from django.urls import path
from django.conf import settings
from .views import *

urlpatterns = [
    path('deposits/', deposits, name='api-deposits'),
    path('sales-persons/', sales_persons, name='api-sales_persons'),
    path('sales-person-transactions/', transactions, name='api-transactions'),
    path('inventory/', inventory, name='api-inventory'),
    path('purchase/', purchase, name='api-purchase'),
    path('confirm-delivery/', confirm_purchase_delivery, name='api-confirm_purchase_delivery'),
    path('supply/', supply, name='api-supply'),
    path('debt/', debt, name='api-debt'),
    path('confirm_deposit/', confirm_deposit, name='api-confirm_deposit'),
    path('swap-product/', swap_product, name='api-swap_product'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
