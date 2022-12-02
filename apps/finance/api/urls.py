from django.urls import path
from django.conf import settings
from .views import *

urlpatterns = [
    path('deposits/', deposits, name='api-deposits'),
    path('inventory/', inventory, name='api-inventory'),
    path('purchase/', purchase, name='api-purchase'),
    path('supply/', supply, name='api-supply'),
    path('debt/', debt, name='api-debt'),
    path('confirm_deposit/', confirm_deposit, name='api-confirm_deposit'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
