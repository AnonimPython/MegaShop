import json
from decimal import Decimal
from django import forms
from .models import Product, Category, ProductImage, ExchangeRate, CategorySpecField


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['sort_order', 'created', 'updated', 'specifications', 'view_count']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.CheckboxInput, forms.SelectMultiple)):
                continue
            field.widget.attrs.update({'class': 'form-control'})

        # Determine category — from POST, instance, or initial
        category_id = None
        if self.is_bound and self.data.get('category'):
            try:
                category_id = int(self.data['category'])
            except (ValueError, TypeError):
                pass
        elif self.instance and self.instance.pk and self.instance.category_id:
            category_id = self.instance.category_id
        elif self.initial.get('category'):
            try:
                category_id = int(self.initial['category'])
            except (ValueError, TypeError):
                pass

        if category_id:
            spec_fields = CategorySpecField.objects.filter(
                category_id=category_id
            )
            existing_specs = {}
            if self.instance and self.instance.pk and self.instance.specifications:
                existing_specs = self.instance.specifications
            elif self.is_bound and self.data.get('specifications'):
                try:
                    existing_specs = json.loads(self.data['specifications'])
                except (json.JSONDecodeError, TypeError):
                    pass

            for sf in spec_fields:
                field_kwargs = {
                    'label': sf.field_name,
                    'required': False,
                    'initial': existing_specs.get(sf.field_name, ''),
                }
                if sf.field_type == 'text':
                    field_kwargs['widget'] = forms.TextInput(attrs={'class': 'form-control', 'placeholder': sf.field_name})
                    self.fields[f'spec_{sf.id}'] = forms.CharField(**field_kwargs)
                elif sf.field_type == 'number':
                    field_kwargs['widget'] = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': sf.field_name})
                    self.fields[f'spec_{sf.id}'] = forms.DecimalField(**field_kwargs)
                elif sf.field_type == 'boolean':
                    field_kwargs.pop('initial', None)
                    field_kwargs['initial'] = existing_specs.get(sf.field_name, False) in (True, 'True', 'true', 'on', 'yes', 1, '1')
                    field_kwargs['widget'] = forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'margin-top: 0.3rem;'})
                    field_kwargs['required'] = False
                    self.fields[f'spec_{sf.id}'] = forms.BooleanField(**field_kwargs)

        # Track spec field count for template
        self.spec_field_count = len([k for k in self.fields.keys() if k.startswith('spec_')])

        # Hide raw JSON field (we use dynamic fields instead)
        if 'specifications' in self.fields:
            self.fields['specifications'].widget = forms.HiddenInput()
            self.fields['specifications'].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Collect spec field values into specifications JSON
        spec_data = {}
        for key, value in self.cleaned_data.items():
            if key.startswith('spec_'):
                field_id = key.replace('spec_', '')
                try:
                    sf = CategorySpecField.objects.get(id=field_id)
                    # Convert Decimal to float for JSON serialization / Конвертируем Decimal в float для JSON
                    if isinstance(value, Decimal):
                        value = float(value)
                    spec_data[sf.field_name] = value
                except CategorySpecField.DoesNotExist:
                    pass
        instance.specifications = spec_data if spec_data else None
        if commit:
            instance.save()
        return instance


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.update({'class': 'form-control'})


class CategorySpecFieldForm(forms.ModelForm):
    class Meta:
        model = CategorySpecField
        fields = ['field_name', 'field_type', 'sort_order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ExchangeRateForm(forms.ModelForm):
    class Meta:
        model = ExchangeRate
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
