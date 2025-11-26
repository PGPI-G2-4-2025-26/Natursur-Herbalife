from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.functions import Coalesce
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from main.populateDB import cargar
from .models import Product, Order, OrderProduct
from .forms import OrderForm
from .service import ProductService, InsufficientStockError
from decimal import Decimal, ROUND_HALF_UP
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import ProductForm
from django.db import IntegrityError, transaction

def list_products(request):
    q = request.GET.get('q', '')
    q = q.strip() if isinstance(q, str) else ''
    if q:
        products = Product.objects.filter(name__icontains=q).exclude(name='(producto eliminado)')
    else:
        products = Product.objects.exclude(name='(producto eliminado)')

    cart_quantities = {}
    order = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        order = Order.objects.filter(status='EN_CARRITO', registered_user=request.user).first()
    else:
        cookie = request.COOKIES.get('anon_user_id')
        if cookie:
            order = Order.objects.filter(status='EN_CARRITO', anonymous_user_cookie=cookie).first()

    if order:
        lines = OrderProduct.objects.filter(order=order)
        for l in lines:
            cart_quantities[l.product.id] = l.quantity

    product_list = []
    for p in products:
        in_cart = cart_quantities.get(p.id, 0)
        max_add = p.stock - in_cart
        if max_add < 0:
            max_add = 0
        setattr(p, 'in_cart_qty', in_cart)
        setattr(p, 'available_stock', p.stock - in_cart if (p.stock - in_cart) > 0 else 0)
        setattr(p, 'max_add', max_add)
        product_list.append(p)

    try:
        page_number = int(request.GET.get('page', 1))
    except (TypeError, ValueError):
        page_number = 1
    paginator = Paginator(product_list, 21)
    products_page = paginator.get_page(page_number)

    return render(request, 'products.html', {'products': products_page, 'q': q})

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
    success_notification = {
        'text': success_message,
        'product_id': product.id,
        'added_qty': added_qty,
    }
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
    ## creo puede refactorizar por order = ProductService.get_active_cart_for_request(request)
    order = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        order = Order.objects.filter(status='EN_CARRITO', registered_user=request.user).first()
    else:
        cookie = request.COOKIES.get('anon_user_id')
        if cookie:
            order = Order.objects.filter(status='EN_CARRITO', anonymous_user_cookie=cookie).first()
    ##

    cart_items = []
    total_price = 0
    if order:
        lines = OrderProduct.objects.filter(order=order)
        for l in lines:
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
            cart_items.append(l)
            total_price += subtotal

    try:
        total_price_display = f"{total_price:.2f}".replace('.', ',')
    except Exception:
        total_price_display = str(total_price)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'total_price_display': total_price_display})

def finalize_order(request):
    order = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        order = Order.objects.filter(status='EN_CARRITO', registered_user=request.user).first()
    else:
        cookie = request.COOKIES.get('anon_user_id')
        if cookie:
            order = Order.objects.filter(status='EN_CARRITO', anonymous_user_cookie=cookie).first()

    if not order:
        messages.error(request, 'No hay ningún pedido en el carrito para finalizar.')
        return redirect('list_products')

    lines = OrderProduct.objects.filter(order=order)
    total_price = 0
    for l in lines:
        unit_price = l.price_at_order if getattr(l, 'price_at_order', None) is not None else l.product.price
        unit_price = Decimal(unit_price)
        qty = int(l.quantity or 0)
        subtotal = (unit_price * qty).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        setattr(l, 'unit_price', unit_price)
        setattr(l, 'subtotal', subtotal)
        setattr(l, 'unit_price_display', f"{unit_price:.2f}".replace('.', ','))
        setattr(l, 'subtotal_display', f"{subtotal:.2f}".replace('.', ','))
        total_price += subtotal

    if request.method == 'GET':
        form = OrderForm(instance=order)
        try:
            total_price_display = f"{total_price:.2f}".replace('.', ',')
        except Exception:
            total_price_display = str(total_price)
        return render(request, 'finalize_order.html', {'form': form, 'order': order, 'cart_items': lines, 'total_price': total_price, 'total_price_display': total_price_display})

    form = OrderForm(request.POST, instance=order)
    if not form.is_valid():
        try:
            total_price_display = f"{total_price:.2f}".replace('.', ',')
        except Exception:
            total_price_display = str(total_price)
        return render(request, 'finalize_order.html', {'form': form, 'order': order, 'cart_items': lines, 'total_price': total_price, 'total_price_display': total_price_display})

    order = form.save(commit=False)
    order.status = 'SOLICITADO'
    order.save()

    try:
        paid_order = ProductService.mark_order_as_paid(order.id)
    except (ValidationError, InsufficientStockError) as e:
        if isinstance(e, InsufficientStockError):
            removed = getattr(e, 'removed', []) or []
        else:
            raw = getattr(e, 'message_dict', {})
            removed = raw.get('insufficient_stock_removed') or raw.get('insufficient_stock') or []
            if removed and isinstance(removed, list) and not all(isinstance(x, dict) for x in removed):
                removed = []
        order.status = 'EN_CARRITO'
        order.save()

        try:
            removed_ids = [int(r.get('line_id')) for r in removed if r.get('line_id')]
        except Exception:
            removed_ids = []
        if removed_ids:
            OrderProduct.objects.filter(id__in=removed_ids).delete()

        lines = OrderProduct.objects.filter(order=order)
        total_price = 0
        for l in lines:
            unit_price = l.price_at_order if getattr(l, 'price_at_order', None) is not None else l.product.price
            unit_price = Decimal(unit_price)
            qty = int(l.quantity or 0)
            subtotal = (unit_price * qty).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            setattr(l, 'unit_price', unit_price)
            setattr(l, 'subtotal', subtotal)
            setattr(l, 'unit_price_display', f"{unit_price:.2f}".replace('.', ','))
            setattr(l, 'subtotal_display', f"{subtotal:.2f}".replace('.', ','))
            total_price += subtotal

        try:
            total_price_display = f"{total_price:.2f}".replace('.', ',')
        except Exception:
            total_price_display = str(total_price)

        if removed:
            item_texts = []
            for r in removed:
                name = r.get('product_name') or r.get('product_ref') or str(r.get('product_id'))
                qty = r.get('quantity_requested') or r.get('requested') or ''
                item_texts.append(f"{name} (cantidad eliminada: {qty})")
            messages.error(request, 'No se pudo completar el pago. Algunos productos ya no estaban disponibles y fueron eliminados del carrito: ' + ', '.join(item_texts))
        else:
            messages.error(request, 'No se pudo completar el pago por falta de stock en algunos productos.')

        form = OrderForm(instance=order)
        return redirect('view_cart')

    try:
        total_price_display = f"{total_price:.2f}".replace('.', ',')
    except Exception:
        total_price_display = str(total_price)
    return render(request, 'order_success.html', {'order': paid_order, 'cart_items': lines, 'total_price': total_price, 'total_price_display': total_price_display})


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
    paginator = Paginator(qs.order_by('date'), per_page)
    pedidos = paginator.get_page(page_number)

    for o in pedidos:
        if not hasattr(o, 'full_name'):
            setattr(o, 'full_name', getattr(o, 'solicitant_name', '') or '')
        if not hasattr(o, 'contact_email'):
            setattr(o, 'contact_email', getattr(o, 'solicitant_contact', '') or '')
        if not hasattr(o, 'telephone'):
            setattr(o, 'telephone', '')
        total_price = Decimal('0.00')
        lines = OrderProduct.objects.filter(order=o).select_related('product').exclude(product__isnull=True).exclude(product__name='(producto eliminado)')
        for l in lines:
            raw_price = l.price_at_order if getattr(l, 'price_at_order', None) is not None else (l.product.price if l.product else 0)
            try:
                unit_price = Decimal(raw_price)
            except Exception:
                unit_price = Decimal('0.00')
            qty = int(l.quantity or 0)
            subtotal = (unit_price * qty).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_price += subtotal
        try:
            total_price_display = f"{total_price:.2f}".replace('.', ',')
        except Exception:
            total_price_display = str(total_price)
        setattr(o, 'total_price', total_price_display)

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
    qs = qs.exclude(status='EN_CARRITO')
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(solicitant_name__icontains=q)

    qs = qs.annotate(total_quantity=Coalesce(Sum('order_products__quantity'), 0))

    page_number = request.GET.get('page', 1)
    paginator = Paginator(qs.order_by('date'), per_page)
    pedidos = paginator.get_page(page_number)

    for o in pedidos:
        if not hasattr(o, 'full_name'):
            setattr(o, 'full_name', getattr(o, 'solicitant_name', '') or '')
        if not hasattr(o, 'contact_email'):
            setattr(o, 'contact_email', getattr(o, 'solicitant_contact', '') or '')
        if not hasattr(o, 'telephone'):
            setattr(o, 'telephone', '')
        total_price = Decimal('0.00')
        lines = OrderProduct.objects.filter(order=o).select_related('product')
        for l in lines:
            raw_price = l.price_at_order if getattr(l, 'price_at_order', None) is not None else (l.product.price if l.product else 0)
            try:
                unit_price = Decimal(raw_price)
            except Exception:
                unit_price = Decimal('0.00')
            qty = int(l.quantity or 0)
            subtotal = (unit_price * qty).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_price += subtotal
        try:
            total_price_display = f"{total_price:.2f}".replace('.', ',')
        except Exception:
            total_price_display = str(total_price)
        setattr(o, 'total_price', total_price_display)

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
                order.solicitant_name = combined

        if email:
            order.solicitant_contact = email
        elif telephone:
            order.solicitant_contact = telephone

        order.save()
        return redirect('show_orders_admin')

    parts = (getattr(order, 'solicitant_name', '') or '').split(' ', 1)
    first_name = parts[0] if parts else ''
    last_name = parts[1] if len(parts) > 1 else ''

    total_price = Decimal('0.00')
    products = OrderProduct.objects.filter(order=order).select_related('product')
    for l in products:
        raw_price = l.price_at_order if getattr(l, 'price_at_order', None) is not None else (l.product.price if l.product else 0)
        try:
            unit_price = Decimal(raw_price)
        except Exception:
            unit_price = Decimal('0.00')
        qty = int(l.quantity or 0)
        subtotal = (unit_price * qty).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_price += subtotal
    try:
        total_price_display = f"{total_price:.2f}".replace('.', ',')
    except Exception:
        total_price_display = str(total_price)
    setattr(order, 'total_price', total_price_display)

    context = {
        'order': order,
        'products': products,
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
            order = Order.objects.get(id=order_id, registered_user_id=user_id)
    except Order.DoesNotExist:
        return redirect('my_orders')

    products = OrderProduct.objects.filter(order=order).select_related('product')
    total_price = Decimal('0.00')
    for l in products:
        raw_price = l.price_at_order if getattr(l, 'price_at_order', None) is not None else (l.product.price if l.product else 0)
        try:
            unit_price = Decimal(raw_price)
        except Exception:
            unit_price = Decimal('0.00')
        qty = int(l.quantity or 0)
        subtotal = (unit_price * qty).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_price += subtotal
    try:
        total_price_display = f"{total_price:.2f}".replace('.', ',')
    except Exception:
        total_price_display = str(total_price)
    setattr(order, 'total_price', total_price_display)

    context = {
        'order': order,
        'products': products,
        'total_price': total_price,
        'total_price_display': total_price_display,
    }
    return render(request, 'order_detail.html', context)


@user_passes_test(lambda u: u.is_staff) 
def admin_orders_list(request):
    orders = Order.objects.all()
    return render(request, 'admin_orders_list.html', {'orders': orders})

def carga(request):
 
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_productos = cargar()
            mensaje="Se han almacenado: " + str(num_productos) +" productos"
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')

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

def remove_from_cart(request, item_id):
    if request.method != 'POST':
        return redirect('view_cart')

    result = ProductService.remove_product_from_cart(item_id)
    return redirect('view_cart')