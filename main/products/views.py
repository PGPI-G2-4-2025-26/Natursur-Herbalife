from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from main.orders.models import OrderProduct
from main.orders.views import list_user_cart_order
from .models import Product
from django.contrib import messages
from .forms import ProductForm
from django.db import transaction

def is_admin(user):
    return user.is_active and user.is_staff

def list_products(request):
    q = request.GET.get('q', '')
    q = q.strip() if isinstance(q, str) else ''
    if q:
        products = Product.objects.filter(name__icontains=q).exclude(name='(producto eliminado)')
    else:
        products = Product.objects.exclude(name='(producto eliminado)')

    cart_quantities = {}
    order = list_user_cart_order(request)
    if order:
        lines = OrderProduct.objects.filter(order=order).select_related('product')
        for l in lines:
            pid = getattr(l.product, 'id', None)
            if pid is not None:
                cart_quantities[pid] = l.quantity

    product_list = []
    for p in products:
        in_cart = cart_quantities.get(p.id, 0)
        max_add = max(p.stock - in_cart, 0)
        setattr(p, 'in_cart_qty', in_cart)
        setattr(p, 'available_stock', max(p.stock - in_cart, 0))
        setattr(p, 'max_add', max_add)
        product_list.append(p)


    page_number = int(request.GET.get('page', 1))
    paginator = Paginator(product_list, 21)
    products_page = paginator.get_page(page_number)

    return render(request, 'products.html', {'products': products_page, 'q': q})


@user_passes_test(is_admin)
def show_product_admin(request):
    q = request.GET.get('q', '').strip()
    per_page = 21

    qs = Product.objects.exclude(name='(producto eliminado)')
    if q:
        qs = qs.filter(name__icontains=q)
    qs = qs.order_by('name')

    page_number = request.GET.get('page', 1)
    paginator = Paginator(qs, per_page)
    products_page = paginator.get_page(page_number)

    return render(request, 'show_products_admin.html', {
        'products': products_page,
        'current_query': q,
    })


@user_passes_test(is_admin)
def create_product_admin(request):

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            prod = form.save(commit=False)
            prod.save()
            messages.success(request, f"Producto '{prod.name}' creado correctamente.")
            return redirect('show_products_admin')
    else:
        form = ProductForm()

    return render(request, 'create_product_admin.html', {'form': form})


@user_passes_test(is_admin)
def edit_product_admin(request, product_id):
    prod = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=prod)
        if form.is_valid():
            prod = form.save(commit=False)
            prod.save()
            messages.success(request, f"Producto '{prod.name}' actualizado correctamente.")
            return redirect('show_products_admin')
    else:
        form = ProductForm(instance=prod)

    return render(request, 'edit_product_admin.html', {'form': form, 'product': prod})


@user_passes_test(is_admin)
def delete_product_admin(request, product_id):
    if request.method != 'POST':
        return redirect('show_products_admin')

    prod = get_object_or_404(Product, id=product_id)
    prod_name = prod.name

    def _snapshot_and_detach(product):
        OrderProduct.objects.filter(product=product, order__status='EN_CARRITO').delete()

        hist_qs = OrderProduct.objects.filter(product=product).exclude(order__status='EN_CARRITO')

        img = getattr(product, 'image', None)
        image_val = None
        if img:
            image_val = getattr(img, 'url', None) or getattr(img, 'name', None)

        for line in hist_qs:
            updated = False
            if not getattr(line, 'product_name', None):
                line.product_name = product.name
                updated = True
            if not getattr(line, 'product_image', None) and image_val:
                line.product_image = image_val
                updated = True
            if not getattr(line, 'price_at_order', None):
                try:
                    line.price_at_order = product.price
                    updated = True
                except Exception:
                    pass
            if updated:
                line.save()

        with transaction.atomic():
            hist_qs.update(product=None)

    _snapshot_and_detach(prod)

    prod.delete()
    messages.success(request, f"Producto '{prod_name}' eliminado correctamente.")
    return redirect('show_products_admin')

