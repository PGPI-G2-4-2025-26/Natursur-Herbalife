from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ProductSolicitation 


class ClientCreationForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name') 

class ProductSolicitationForm(forms.ModelForm):

    class Meta:
        model = ProductSolicitation
        fields = ['solicitant_name', 'solicitant_contact']

        labels = {
            'solicitant_name': 'Full Name',
            'solicitant_contact': 'Email or Phone Number (for contact)',
        }