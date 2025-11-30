from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from main.orders.models import Order, OrderProduct
from .models import Product
from django.contrib import messages
from .forms import ProductForm
from django.db import IntegrityError, transaction
from main.orders.service import ProductService

def list_products(request):
    q = request.GET.get('q', '')
    q = q.strip() if isinstance(q, str) else ''
    if q:
        products = Product.objects.filter(name__icontains=q).exclude(name='(producto eliminado)')
    else:
        products = Product.objects.exclude(name='(producto eliminado)')

    cart_quantities = {}
    order = ProductService.get_active_cart_for_request(request)
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

    try:
        page_number = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page_number = 1
    paginator = Paginator(product_list, 21)
    products_page = paginator.get_page(page_number)

    return render(request, 'products.html', {'products': products_page, 'q': q})


@login_required
def show_product_admin(request):
    if not request.user.is_staff:
        return redirect('list_products')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            try:
                pid = int(request.POST.get('product_id'))
                prod = Product.objects.get(id=pid)
                prod_name = prod.name
                prod.delete()
                messages.success(request, f"Producto '{prod_name}' eliminado correctamente.")
                base = reverse('show_products_admin')
                q = request.GET.get('q', '')
                per_page = request.GET.get('per_page', '')
                params = []
                if q:
                    params.append(f"q={q}")
                if per_page:
                    params.append(f"per_page={per_page}")
                if params:
                    return redirect(base + '?' + '&'.join(params))
                return redirect(base)
            except (Product.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'No se pudo eliminar el producto.')

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


@login_required
def create_product_admin(request):
    if not request.user.is_staff:
        return redirect('list_products')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            prod = form.save(commit=False)
            if getattr(prod, 'stock', None) is None:
                prod.stock = 0
            prod.save()
            messages.success(request, f"Producto '{prod.name}' creado correctamente.")
            return redirect('show_products_admin')
    else:
        form = ProductForm()

    return render(request, 'create_product_admin.html', {'form': form})


@login_required
def edit_product_admin(request, product_id):
    if not request.user.is_staff:
        return redirect('list_products')

    try:
        prod = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, 'Producto no encontrado.')
        return redirect('show_products_admin')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=prod)
        if form.is_valid():
            prod = form.save(commit=False)
            if getattr(prod, 'stock', None) is None:
                prod.stock = 0
            prod.save()
            messages.success(request, f"Producto '{prod.name}' actualizado correctamente.")
            return redirect('show_products_admin')
        else:
            messages.error(request, 'Hay errores en el formulario. Revísalos e inténtalo de nuevo.')
    else:
        form = ProductForm(instance=prod)

    return render(request, 'edit_product_admin.html', {'form': form, 'product': prod})


@login_required
def delete_product_admin(request, product_id):
    """Delete a product (admin only). Accepts POST only and redirects back to admin list."""
    if not request.user.is_staff:
        return redirect('list_products')

    if request.method != 'POST':
        return redirect('show_products_admin')

    try:
        prod = Product.objects.get(id=product_id)
        prod_name = prod.name

        cart_lines = OrderProduct.objects.filter(product=prod, order__status='EN_CARRITO')
        if cart_lines.exists():
            cart_lines.delete()

        hist_lines = OrderProduct.objects.filter(product=prod).exclude(order__status='EN_CARRITO')
        for l in hist_lines:
            changed = False
            if not getattr(l, 'product_name', None):
                l.product_name = prod.name
                changed = True
            if not getattr(l, 'product_image', None):
                img = getattr(prod, 'image', None)
                if img:
                    try:
                        l.product_image = img.url
                    except Exception:
                        l.product_image = getattr(img, 'name', None)
                    changed = True
            if not getattr(l, 'price_at_order', None):
                try:
                    l.price_at_order = prod.price
                    changed = True
                except Exception:
                    pass
            if changed:
                l.save()

        try:
            with transaction.atomic():
                hist_lines.update(product=None)
        except IntegrityError:
            placeholder, _ = Product.objects.get_or_create(
                name='(producto eliminado)',
                defaults={
                    'ref': None,
                    'price': 0,
                    'flavor': None,
                    'size': None,
                    'stock': 0,
                }
            )
            hist_lines.update(product=placeholder)

        prod.delete()
        messages.success(request, f"Producto '{prod_name}' eliminado correctamente.")
    except Product.DoesNotExist:
        messages.error(request, 'Producto no encontrado.')

    return redirect('show_products_admin')

