from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import re
from .models import UserProfile 


class ClientCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'placeholder': 'correo@ejemplo.com',
            'class': 'form-control',
        }),
        error_messages={
            'required': _("El correo electrónico es obligatorio."),
            'invalid': _("Por favor, introduce un correo válido."), 
        }
    )
    
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        error_messages = {
            'username': {
                'required': _("El nombre de usuario es obligatorio."),
                'unique': _("Este nombre de usuario ya está en uso."),
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de Usuario',
            'autofocus': True
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Ya existe una cuenta registrada con este correo."))
        return email


class ClientLoginForm(AuthenticationForm):
    error_messages = {'invalid_login': _("Usuario o contraseña incorrectos.")}
    username = forms.CharField(label=_('Usuario'), widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(label=_('Contraseña'), widget=forms.PasswordInput(attrs={'class': 'form-control'}))



class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'photo']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono',
                'pattern': r'^\+?[0-9]{9,15}$', 
                'title': 'Introduce tu número de teléfono.'
            }),
        'photo': forms.FileInput(attrs={'id': 'id_photo'}),       
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        
        if not phone:
            return phone

        phone = phone.strip()

        if not re.match(r'^\+?\d{9,15}$', phone):
            raise ValidationError(_("Introduce un número de teléfono válido."))

        return phone