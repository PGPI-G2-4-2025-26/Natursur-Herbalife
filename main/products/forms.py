from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

from .models import Order, Product


class OrderForm(forms.ModelForm):
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
        required=True,
        min_length=6,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Dirección de envío'}),
        error_messages={
            'required': 'La dirección es obligatoria.',
            'min_length': 'Introduce una dirección válida (más caracteres).',
        }
    )

    class Meta:
        model = Order
        fields = ['solicitant_name', 'solicitant_contact', 'solicitant_address']

    def clean_solicitant_name(self):
        name = self.cleaned_data.get('solicitant_name', '')
        name = name.strip()
        if len(name) < 3:
            raise ValidationError('El nombre es demasiado corto.')
        if any(ch.isdigit() for ch in name):
            raise ValidationError('El nombre no puede contener dígitos.')
        return name

    def clean_solicitant_contact(self):
        contact = self.cleaned_data.get('solicitant_contact', '')
        contact = contact.strip()
        if not contact:
            raise ValidationError('El contacto es obligatorio.')

        if '@' in contact:
            try:
                validate_email(contact)
            except ValidationError:
                raise ValidationError('Introduce un correo electrónico válido.')
            return contact

        phone_re = re.compile(r'^\+?[0-9\s\-()]{7,}$')
        if not phone_re.match(contact):
            raise ValidationError('Introduce un teléfono válido (dígitos, espacios, +, - o paréntesis).')

        return contact

    def clean_solicitant_address(self):
        addr = self.cleaned_data.get('solicitant_address', '')
        addr = addr.strip()
        if len(addr) < 6:
            raise ValidationError('La dirección es demasiado corta.')
        return addr
    
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