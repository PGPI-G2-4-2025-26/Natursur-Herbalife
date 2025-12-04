from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.functions import Coalesce
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from django.db import transaction
from main.orders.models import Order, OrderProduct
from main.products.models import Product
from .forms import OrderForm
from main.orders.service import ProductService
from decimal import Decimal, ROUND_HALF_UP
from django.contrib import messages
import datetime
import uuid

def is_admin(user):
    return user.is_active and user.is_staff

def list_user_cart_order(request):
    order = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        order = Order.objects.filter(status='EN_CARRITO', registered_user=request.user).first()
    else:
        cookie = request.COOKIES.get('anon_user_id')
        if cookie:
            order = Order.objects.filter(status='EN_CARRITO', anonymous_user_cookie=cookie).first()
    return order


def _format_price(value):
    try:
        return f"{value:.2f}".replace('.', ',')
    except Exception:
        return str(value)


def _prepare_order_lines(order, exclude_deleted=False):
    qs = OrderProduct.objects.filter(order=order).select_related('product')
    if exclude_deleted:
        qs = qs.exclude(product__isnull=True).exclude(product__name='(producto eliminado)')

    items = []
    total = Decimal('0.00')
    for l in qs:
        raw_price = l.price_at_order if getattr(l, 'price_at_order', None) is not None else (l.product.price if l.product else 0)
        try:
            unit_price = Decimal(raw_price)
        except Exception:
            unit_price = Decimal('0.00')
        qty = int(l.quantity or 0)
        subtotal = (unit_price * qty).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        setattr(l, 'unit_price', unit_price)
        setattr(l, 'subtotal', subtotal)
        setattr(l, 'unit_price_display', f"{unit_price:.2f}".replace('.', ','))
        setattr(l, 'subtotal_display', f"{subtotal:.2f}".replace('.', ','))
        items.append(l)
        total += subtotal

    return items, total


def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('list_products')

    q = request.POST.get('q', '')
    q = q.strip() if isinstance(q, str) else ''

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    product = Product.objects.get(id=product_id)

    order_line, anon_cookie = ProductService.add_product_to_cart(request, {
        'id': product.id,
        'name': product.name,
        'ref': product.ref,
        'price': product.price,
        'flavor': product.flavor,
        'size': product.size,
        'image': product.image,
    }, requested_quantity=quantity)

    added_qty = 0
    if order_line:
        added_qty = min(quantity, order_line.quantity)

    success_message = f"Se han añadido {added_qty} {product.name}"
    messages.success(request, success_message)

    page = request.POST.get('page', request.GET.get('page', '1'))

    base = reverse('list_products')
    qs = f"?page={page}"
    if q:
        qs += f"&q={q}"

    fragment = f"#product-{product.id}"
    redirect_url = f"{base}{qs}{fragment}"

    resp = redirect(redirect_url)
    if anon_cookie:
        resp.set_cookie('anon_user_id', anon_cookie, max_age=60*60*24*30)
    return resp

def view_cart(request):
    order = list_user_cart_order(request)
    cart_items = []
    total_price = Decimal('0.00')
    if order:
        cart_items, total_price = _prepare_order_lines(order)

    total_price_display = _format_price(total_price)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'total_price_display': total_price_display})

def remove_from_cart(request, item_id):
    if request.method != 'POST':
        return redirect('view_cart')

    result = ProductService.remove_product_from_cart(item_id)
    return redirect('view_cart')

def _mark_order_as_paid(order):
    """Marca un orden como pagado y actualiza el stock. Retorna (success, removed_items)."""
    if order.is_paid:
        return True, []
    
    shortages = []
    lines = OrderProduct.objects.filter(order=order)
    
    for line in lines:
        prod = line.product
        qty = int(line.quantity or 0)
        available = int(prod.stock or 0)
        if qty > available:
            shortages.append({
                'line_id': line.id,
                'product_id': prod.id,
                'product_ref': prod.ref,
                'product_name': prod.name,
                'quantity_requested': qty,
                'available': available,
            })
    
    if shortages:
        return False, shortages
    
    # Generar ID único si no existe
    if not order.order_identified:
        for _ in range(10):
            candidate = f"ORD-{uuid.uuid4().hex[:12].upper()}"
            if not Order.objects.filter(order_identified=candidate).exists():
                order.order_identified = candidate
                break
        else:
            order.order_identified = f"ORD-{int(datetime.datetime.utcnow().timestamp())}-{uuid.uuid4().hex[:6].upper()}"
    
    # Reducir stock de productos
    with transaction.atomic():
        for line in lines:
            prod = line.product
            qty = int(line.quantity or 0)
            if qty > 0:
                new_stock = max((prod.stock or 0) - qty, 0)
                prod.stock = new_stock
                prod.save()
        
        order.is_paid = True
        order.save()
    
    return True, []


def finalize_order(request):
    order = list_user_cart_order(request)

    if not order:
        messages.error(request, 'No hay ningún pedido en el carrito para finalizar.')
        return redirect('list_products')

    lines, total_price = _prepare_order_lines(order)

    if request.method == 'GET':
        form = OrderForm(instance=order)
        total_price_display = _format_price(total_price)
        return render(request, 'finalize_order.html', {
            'form': form, 'order': order, 'cart_items': lines, 
            'total_price': total_price, 'total_price_display': total_price_display
        })

    form = OrderForm(request.POST, instance=order)
    if not form.is_valid():
        total_price_display = _format_price(total_price)
        return render(request, 'finalize_order.html', {
            'form': form, 'order': order, 'cart_items': lines, 
            'total_price': total_price, 'total_price_display': total_price_display
        })

    order = form.save(commit=False)
    order.status = 'SOLICITADO'
    order.save()

    success, removed_items = _mark_order_as_paid(order)
    
    if not success:
        order.status = 'EN_CARRITO'
        order.save()
        
        removed_ids = [item['line_id'] for item in removed_items]
        if removed_ids:
            OrderProduct.objects.filter(id__in=removed_ids).delete()
        
        item_texts = []
        for item in removed_items:
            name = item.get('product_name') or item.get('product_ref') or str(item.get('product_id'))
            qty = item.get('quantity_requested', '')
            item_texts.append(f"{name} (cantidad solicitada: {qty})")
        
        messages.error(request, 'No se pudo completar el pago. Algunos productos ya no estaban disponibles y fueron eliminados del carrito: ' + ', '.join(item_texts))
        return redirect('view_cart')
    
    lines, total_price = _prepare_order_lines(order)
    total_price_display = _format_price(total_price)
    return render(request, 'order_success.html', {
        'order': order, 'cart_items': lines, 
        'total_price': total_price, 'total_price_display': total_price_display
    })


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
    qs = Order.objects.filter(registered_user_id=user_id)
    qs = qs.exclude(status='EN_CARRITO')
    if status:
        qs = qs.filter(status=status)

    qs = qs.annotate(
        total_quantity=Coalesce(
            Sum('order_products__quantity', filter=Q(order_products__product__isnull=False) & ~Q(order_products__product__name='(producto eliminado)')),
            0
        )
    )

    page_number = request.GET.get('page', 1)
    paginator = Paginator(qs.order_by('-date'), per_page)
    orders = paginator.get_page(page_number)

    for order in orders:
        _, total_price = _prepare_order_lines(order, exclude_deleted=True)
        total_price_display = _format_price(total_price)
        setattr(order, 'total_price', total_price_display)

    context = {
        'orders': orders,
        'current_status': status,
        'current_per_page': per_page,
    }
    return render(request, 'show_orders.html', context)


@user_passes_test(is_admin)
def show_orders_admin(request):

    status = request.GET.get('status', '')
    q = request.GET.get('q', '').strip()

    try:
        per_page = int(request.GET.get('per_page', 10))
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 25, 50):
        per_page = 10

    qs = Order.objects.all()
    qs = qs.exclude(status='EN_CARRITO')
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(solicitant_name__icontains=q)

    qs = qs.annotate(total_quantity=Coalesce(Sum('order_products__quantity'), 0))

    page_number = request.GET.get('page', 1)
    paginator = Paginator(qs.order_by('-date'), per_page)
    orders = paginator.get_page(page_number)

    for pedido in orders:
        _, total_price = _prepare_order_lines(pedido)
        total_price_display = _format_price(total_price)
        setattr(pedido, 'total_price', total_price_display)

    context = {
        'orders': orders,
        'current_status': status,
        'current_query': q,
        'current_per_page': per_page,
    }
    return render(request, 'show_orders_admin.html', context)


@user_passes_test(is_admin)
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')

    if new_status in dict(Order.STATUS_CHOICES).keys():
        order.status = new_status
    
    order.save()
    return redirect('show_orders_admin')


@user_passes_test(is_admin)
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('show_orders_admin')


@login_required
def order_detail(request, order_id):
    user_id = request.user.id

    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, registered_user_id=user_id)

    products, total_price = _prepare_order_lines(order)
    total_price_display = _format_price(total_price)
    setattr(order, 'total_price', total_price_display)

    context = {
        'order': order,
        'products': products,
        'total_price': total_price,
        'total_price_display': total_price_display,
    }
    if request.path.endswith('/editar/'):
        return render(request, 'edit_order.html', context)
    return render(request, 'order_detail.html', context)
