from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class ClientCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'correo@ejemplo.com',
        'class': 'form-control',
    }))

    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Nombre',
        'class': 'form-control',
    }))

    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apellidos',
        'class': 'form-control',
    }))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe un usuario registrado con ese email.')
        return email


class ClientLoginForm(AuthenticationForm):

    error_messages = {
        'invalid_login': _("Usuario o contraseña incorrectos."),
    }

    username = forms.CharField(
        label=_('Usuario'),
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'placeholder': 'Usuario',
            'class': 'form-control',
        }),
        error_messages={
            'required': _("Por favor, escribe tu usuario."),
        }
    )

    password = forms.CharField(
        label=_('Contraseña'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'form-control',
        }),
        error_messages={
            'required': _("Por favor, escribe tu contraseña."),
        }
    )