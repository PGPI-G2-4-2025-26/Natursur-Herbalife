from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from main.orders.models import Order

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
