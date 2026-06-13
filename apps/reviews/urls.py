from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
]
