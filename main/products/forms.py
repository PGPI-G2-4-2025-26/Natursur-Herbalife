from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'flavor', 'size', 'stock', 'image', 'ref']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nombre del producto'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'flavor': forms.TextInput(attrs={'placeholder': 'Sabor'}),
            'size': forms.TextInput(attrs={'placeholder': 'Tamaño (p. ej. 500 g)'}),
            'stock': forms.NumberInput(attrs={'min': '0', 'step': '1', 'placeholder': '50'}),
            'ref': forms.TextInput(attrs={'placeholder': 'Referencia / enlace'}),
        }
        labels = {
            'name': 'Nombre',
            'price': 'Precio',
            'flavor': 'Sabor (opcional)',
            'size': 'Tamaño (opcional)',
            'image': 'Imagen',
            'ref': 'Referencia (opcional)',
            'stock': 'Stock'
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('El nombre es obligatorio.')
        return name

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise forms.ValidationError('El precio es obligatorio.')
        if price < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None:
            raise forms.ValidationError('La cantidad de stock es obligatoria.')
        try:
            stock_int = int(stock)
        except (TypeError, ValueError):
            raise forms.ValidationError('Introduce un número entero válido para el stock.')
        if stock_int < 0:
            raise forms.ValidationError('El stock no puede ser negativo.')
        return stock_int