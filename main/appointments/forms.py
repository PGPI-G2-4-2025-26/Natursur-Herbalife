from django import forms

class CreateAppointmentForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Appointment Name',
            'class': 'form-control',
        })
    )
    price = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Price',
            'class': 'form-control',
        })
    )
    duration = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'placeholder': 'Duration in minutes',
            'class': 'form-control',
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Description',
            'class': 'form-control',
        })
    )
    premium = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )

class CreateDiscountForm(forms.Form):
    discount = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Discount price',
            'class': 'form-control',
        })
    )

    current_end_date = forms.CharField(
        label="Fecha fin de descuento actual",
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
        label="Nueva fecha fin de descuento",
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
