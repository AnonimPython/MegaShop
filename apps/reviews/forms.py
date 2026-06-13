from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['pros', 'cons', 'text', 'rating']
        widgets = {
            'pros': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'What did you like? Battery life, screen, camera...'
            }),
            'cons': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'What could be better? Software, weight, price...'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Overall impression...'
            }),
            'rating': forms.Select(attrs={'class': 'form-control'}, choices=[
                (5, '5 ★ Excellent'),
                (4, '4 ★ Good'),
                (3, '3 ★ Average'),
                (2, '2 ★ Poor'),
                (1, '1 ★ Terrible'),
            ]),
        }
