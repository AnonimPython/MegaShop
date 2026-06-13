from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    path('set-store/', views.set_current_store, name='set_store',),
]
