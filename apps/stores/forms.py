#? Store forms / Формы для магазинов
from django import forms
from .models import Store


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = [
            'name', 'slug', 'address', 'phone',
            'email', 'city', 'work_hours', 'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'work_hours': forms.TextInput(attrs={'class': 'form-control'}),
        }
