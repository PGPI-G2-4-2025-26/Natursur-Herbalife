from django import forms


class CreateAppointmentForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre de la sesión',
            'class': 'form-control',
        })
    )
    price = forms.DecimalField(
        max_digits=8,
        label='Precio',
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'precio',
            'class': 'form-control',
        })
    )
    duration = forms.IntegerField(
        label='Duración',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Duración en minutos',
            'class': 'form-control',
        })
    )
    description = forms.CharField(
        required=False,
        label='Descripción',
        widget=forms.Textarea(attrs={
            'placeholder': 'Descripción',
            'class': 'form-control',
        })
    )
    premium = forms.BooleanField(
        label='Premium',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )


class CreateDiscountForm(forms.Form):
    discount = forms.DecimalField(
        max_digits=5,
        label='Precio',
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Precio del descuento',
            'class': 'form-control',
        })
    )

    current_end_date = forms.CharField(
        label="Fecha de fin de descuento actual",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'style': '''
                background-color: #e9ecef; 
                font-weight: bold;
                width: auto;            
                field-sizing: content;
                height: auto;
            '''
        })
    )

    endDiscount = forms.DateTimeField(
        label="Nueva fecha de fin de descuento",
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
