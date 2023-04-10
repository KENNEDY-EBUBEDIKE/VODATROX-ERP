from django.urls import path
from django.conf import settings
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('users-list/', users_list, name='api-users_list'),
    path('register/', update_profile, name='api-register'),

    path('user/', user, name='api-user'),
    path('change-status/', change_status, name='api-change_status'),
    path('add-sales-persons/', add_to_sales_persons, name='api-add_to_sales_persons'),

    path('login/', login, name='api-login'),
    path('logout/', LogoutView.as_view(), name='api-login'),

]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
