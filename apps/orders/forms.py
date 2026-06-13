from django import forms
from .models import Order
from apps.stores.models import Store


class OrderCreateForm(forms.ModelForm):
    pickup_store = forms.ModelChoiceField(
        queryset=Store.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'pickupStoreSelect'}),
        label='Pickup store',
    )

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'delivery_type', 'pickup_store',
            'city', 'address', 'postal_code',
            'delivery_floor', 'delivery_apartment', 'backup_phone',
            'comment', 'payment_method',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            if 'form-control' not in existing:
                field.widget.attrs.update({'class': 'form-control'})
        # delivery_type radio
        self.fields['delivery_type'].widget = forms.RadioSelect(
            attrs={'class': 'form-check-input', 'onchange': 'toggleDelivery(this.value)'},
            choices=Order.DELIVERY_CHOICES,
        )
        self.fields['delivery_type'].initial = 'pickup'
        self.fields['comment'].widget.attrs.update({'rows': 3})
        self.fields['address'].required = False
        self.fields['city'].required = False

    def clean(self):
        cleaned = super().clean()
        delivery_type = cleaned.get('delivery_type')
        if delivery_type == 'delivery':
            if not cleaned.get('address'):
                self.add_error('address', 'Address is required for home delivery.')
            if not cleaned.get('city'):
                self.add_error('city', 'City is required for home delivery.')
        return cleaned
