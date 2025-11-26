from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from .models import Order, Product

class OrderForm(forms.ModelForm):
    FIXED_ADDRESS_MESSAGE = "Los envíos a domicilio no están disponibles aún. Recogida en tienda disponible en la oficina de Natursur."

    solicitant_name = forms.CharField(
        label='Nombre completo',
        required=True,
        min_length=3,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
        error_messages={
            'required': 'El nombre es obligatorio.',
            'min_length': 'Introduce al menos 3 caracteres para el nombre.',
        }
    )

    solicitant_contact = forms.CharField(
        label='Email o Número de teléfono (para contacto)',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Correo electrónico o teléfono'}),
        error_messages={
            'required': 'El contacto (email o teléfono) es obligatorio.',
        }
    )

    solicitant_address = forms.CharField(
        label='Dirección de envío',
        required=False, 
        widget=forms.Textarea(attrs={
            'rows': 1, 
            'readonly': 'readonly', 
            'class': 'form-control',
            'style': 'background-color: #e9ecef; color: #495057; cursor: not-allowed; resize: none;'
        })
    )

    class Meta:
        model = Order
        fields = ['solicitant_name', 'solicitant_contact', 'solicitant_address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['solicitant_address'] = self.FIXED_ADDRESS_MESSAGE

    def clean_solicitant_name(self):
        return self.cleaned_data.get('solicitant_name', '').strip()

    def clean_solicitant_contact(self):
        return self.cleaned_data.get('solicitant_contact', '').strip()

    def clean_solicitant_address(self):
        return self.FIXED_ADDRESS_MESSAGE

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