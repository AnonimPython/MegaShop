from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('products/export/csv/', views.product_export_csv, name='product_export_csv'),
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.order_update_status, name='order_update_status'),
    # Users
    path('users/', views.user_list, name='user_list'),
    # Reviews
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/<int:review_id>/moderate/', views.review_moderate, name='review_moderate'),
    # Stores (expansion manager + admin)
    path('stores/', views.store_list, name='store_list'),
    path('stores/create/', views.store_create, name='store_create'),
    path('stores/<int:store_id>/edit/', views.store_edit, name='store_edit'),
    path('stores/<int:store_id>/delete/', views.store_delete, name='store_delete'),
    path('stores/<int:store_id>/staff/', views.store_staff, name='store_staff'),
    path('stores/<int:store_id>/stock/', views.store_stock, name='store_stock'),
    # Category spec fields
    path('categories/<int:category_id>/spec-fields/', views.category_spec_field_list, name='category_spec_field_list'),
    path('categories/<int:category_id>/spec-fields/create/', views.category_spec_field_edit, name='category_spec_field_create'),
    path('categories/<int:category_id>/spec-fields/<int:field_id>/edit/', views.category_spec_field_edit, name='category_spec_field_edit'),
    path('categories/<int:category_id>/spec-fields/<int:field_id>/delete/', views.category_spec_field_delete, name='category_spec_field_delete'),
    # Exchange rates
    path('exchange-rates/', views.exchange_rate_list, name='exchange_rate_list'),
    path('exchange-rates/create/', views.exchange_rate_edit, name='exchange_rate_create'),
    path('exchange-rates/<int:rate_id>/edit/', views.exchange_rate_edit, name='exchange_rate_edit'),
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/export/<str:period>/', views.export_sales_excel, name='export_sales_excel'),
]
