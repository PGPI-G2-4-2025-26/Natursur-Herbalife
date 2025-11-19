from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from main.populateDB import cargar
from .models import Product, ProductSolicitation
from .forms import ProductSolicitationForm
from .service import ProductService

def list_products(request):
    products =  Product.objects.all()
    return render(request, 'products.html', {'products': products})

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    solicitation = ProductService.add_product_to_cart({
        'id': product.id,
        'name': product.name,
        'ref': product.ref,
        'price': product.price,
        'flavor': product.flavor,
        'size': product.size,
        'image': product.image,
    })
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

## @user_passes_test(lambda u: u.is_staff) Descomentar al implementar gestión de usuarios
def carga(request):
 
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_productos = cargar()
            mensaje="Se han almacenado: " + str(num_productos) +" productos"
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')