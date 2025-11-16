from django import forms
from .models import ProductSolicitation 

class ProductSolicitationForm(forms.ModelForm):

    class Meta:
        model = ProductSolicitation
        fields = ['solicitant_name', 'solicitant_contact']

        labels = {
            'solicitant_name': 'Full Name',
            'solicitant_contact': 'Email or Phone Number (for contact)',
        }