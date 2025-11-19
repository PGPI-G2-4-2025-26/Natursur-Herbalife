import os
from django.conf import settings
from django.db import connection
from django.shortcuts import redirect, render
from .models import Appointment
from django.contrib.admin.views.decorators import staff_member_required
from . import forms as appointment_forms
from django.utils import formats

def appointments(request):
    appointments = Appointment.objects.all()
    return render(request, 'appointments.html', {'appointments': appointments})

@staff_member_required(login_url='appointments')
def create_appointment(request):
    if request.method == 'POST':
        form = appointment_forms.CreateAppointmentForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            appointment = Appointment(
                name=cd.get('name'),
                price=cd.get('price'),
                duration=cd.get('duration'),
                description=cd.get('description', ''),
                premium=cd.get('premium', False)
            )
            appointment.full_clean()
            appointment.save()
            return redirect('appointments')
    else:
        form = appointment_forms.CreateAppointmentForm()

    return render(request, 'create_appointment.html', {'form': form})

@staff_member_required(login_url='appointments')
def update_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    if request.method == 'POST':
        form = appointment_forms.CreateAppointmentForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            appointment.name = cd.get('name')
            appointment.price = cd.get('price')
            appointment.duration = cd.get('duration')
            appointment.description = cd.get('description', '')
            appointment.premium = cd.get('premium', False)
            appointment.full_clean()
            appointment.save()
            return redirect('appointments')
    else:
        initial = {
            'name': appointment.name,
            'price': appointment.price,
            'duration': appointment.duration,
            'description': appointment.description,
            'premium': appointment.premium,
        }
        form = appointment_forms.CreateAppointmentForm(initial=initial)

    return render(request, 'update_appointment.html', {'appointment': appointment, 'form': form})

@staff_member_required(login_url='appointments')
def delete_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    appointment.delete()
    return redirect('appointments')

@staff_member_required(login_url='appointments')
def create_discount(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    if request.method == 'POST':
        form = appointment_forms.CreateDiscountForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            appointment.discount = cd.get('discount')
            appointment.endDiscount = cd.get('endDiscount')
            appointment.save()
            return redirect('appointments')
    else:
        formatted_date_text = "Sin fecha asignada"
        
        if appointment.endDiscount:
            formatted_date_text = formats.date_format(
                appointment.endDiscount, 
                format='d \d\e F \d\e\l Y \\a \l\\a\s H:i'
            )
        
        print("Formatted date text:", formatted_date_text)
        initial = {
            'discount': appointment.discount,
            'current_end_date': formatted_date_text,
        }
        form = appointment_forms.CreateDiscountForm(initial=initial)

    return render(request, 'create_discount.html', {'appointment': appointment, 'form': form})
