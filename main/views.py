from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings

from .models import Product, ProductSolicitation, Testimonial
from .forms import ClientCreationForm, ProductSolicitationForm 


def registration(request):
    form = ClientCreationForm()
    return render(request, 'registration.html', {'form': form})

def login(request):
    return render(request, 'login.html')

def home(request):
    testimonials = Testimonial.objects.all()[:1] 
    context = {
        'testimonials': testimonials,
        'MEDIA_URL': settings.MEDIA_URL 
    }
    return render(request, 'home.html', context)

def services(request):
    return render(request, 'services.html') 


def list_products(request):
    products = Product.objects.all()[:0] 
    return render(request, 'products.html', {'products': products})

def add_to_cart(request, product_id):
    messages.info(request, f"Producto {product_id} añadido simuladamente.")
    return redirect('view_cart')

def view_cart(request):
    return render(request, 'cart.html') 

def finalize_solicitation(request):
    form = ProductSolicitationForm()
    return render(request, 'finalize_solicitation.html', {'form': form})


@login_required
def my_solicitations(request):
    solicitations = ProductSolicitation.objects.none()
    return render(request, 'my_solicitations.html', {'solicitations': solicitations})

@user_passes_test(lambda u: u.is_staff) 
def admin_solicitations_list(request):
    solicitations = ProductSolicitation.objects.none()
    return render(request, 'admin_solicitations_list.html', {'solicitations': solicitations})