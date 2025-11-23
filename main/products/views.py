from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.functions import Coalesce
from django.db.models import Sum
from django.core.paginator import Paginator
from main.populateDB import cargar
from .models import Order, OrderProduct, Product, ProductSolicitation
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
def show_orders(request):
    user_id = request.user.id
    status = request.GET.get('status', '')
    try:
        per_page = int(request.GET.get('per_page', 10))
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 25, 50):
        per_page = 10
    qs = Order.objects.filter(user=user_id)
    qs = qs.exclude(status='EN_CARRITO')
    if status:
        qs = qs.filter(status=status)

    qs = qs.annotate(total_quantity=Coalesce(Sum('orderproduct__quantity'), 0))

    page_number = request.GET.get('page', 1)
    paginator = Paginator(qs.order_by('date'), per_page)
    pedidos = paginator.get_page(page_number)

    context = {
        'orders': pedidos,              
        'pedidos': pedidos,              
        'current_status': status,
        'current_per_page': per_page,
    }
    return render(request, 'my_orders.html', context)

@login_required
def show_orders_admin(request):
    if not request.user.is_staff:
        return redirect('my_orders')
    status = request.GET.get('status', '')
    q = request.GET.get('q', '').strip()

    try:
        per_page = int(request.GET.get('per_page', 10))
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 25, 50):
        per_page = 10

    qs = Order.objects.all() 
    qs = Order.objects.exclude(status='EN_CARRITO')
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(full_name__icontains=q)

    qs = qs.annotate(total_quantity=Coalesce(Sum('orderproduct__quantity'), 0))

    page_number = request.GET.get('page', 1)
    paginator = Paginator(qs.order_by('date'), per_page)
    pedidos = paginator.get_page(page_number)

    context = {
        'orders': pedidos,
        'pedidos': pedidos,
        'current_status': status,
        'current_query': q,
        'current_per_page': per_page,
    }
    return render(request, 'show_orders_admin.html', context)
    
@login_required
def edit_order(request, order_id):
    if not request.user.is_staff:
        return redirect('my_orders')
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect('show_orders_admin')

    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            order.delete()
            return redirect('show_orders_admin')

        new_status = request.POST.get('status')
        first = request.POST.get('first_name', '').strip()
        last = request.POST.get('last_name', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        email = request.POST.get('contact_email', '').strip()

        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status

        if first or last:
            combined = (first + ' ' + last).strip()
            if combined:
                order.full_name = combined

        if telephone:
            order.telephone = telephone
        if email:
            order.contact_email = email

        order.save()
        return redirect('show_orders_admin')

    parts = order.full_name.split(' ', 1)
    first_name = parts[0] if parts else ''
    last_name = parts[1] if len(parts) > 1 else ''

    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
        'first_name': first_name,
        'last_name': last_name,
    }
    return render(request, 'edit_order.html', context)

@login_required
def order_detail(request, order_id):
    user_id = request.user.id
    try:
        if request.user.is_staff:
            order = Order.objects.get(id=order_id)
        else:
            order = Order.objects.get(id=order_id, user_id=user_id)
    except Order.DoesNotExist:
        return redirect('my_orders')

    products = OrderProduct.objects.filter(order=order).select_related('product')
    context = {
        'order': order,
        'products': products,
    }
    return render(request, 'order_detail.html', context)

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