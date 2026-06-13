from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path, include
from apps.catalog import views as catalog_views

urlpatterns = [
    path('', catalog_views.product_list, name='home'),
    path('accounts/', include('apps.accounts.urls')),
    path('catalog/', include('apps.catalog.urls')),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('stores/', include('apps.stores.urls')),
    path('admin-panel/', include('apps.admin_panel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
