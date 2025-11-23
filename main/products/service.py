from .models import Product, Order, OrderProduct
import datetime
from django.db import transaction
import uuid


class ProductService:


    @transaction.atomic
    def add_product_to_cart(request, product_data, requested_quantity=1):
        anon_cookie_to_set = None
        product_id = product_data.get('id')

        product = None
        if product_id:
            product = Product.objects.filter(id=product_id).first()
        if not product:
            product_vals = {k: v for k, v in product_data.items() if k in ['name', 'ref', 'price', 'flavor', 'size', 'image']}
            product, _ = Product.objects.get_or_create(ref=product_vals.get('ref'), defaults=product_vals)

        order = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            order = Order.objects.filter(status='EN_CARRITO', registered_user=request.user).first()
        else:
            cookie = request.COOKIES.get('anon_user_id')
            if cookie:
                order = Order.objects.filter(status='EN_CARRITO', anonymous_user_cookie=cookie).first()


        if not order:
            if not (hasattr(request, 'user') and request.user.is_authenticated):
                cookie = request.COOKIES.get('anon_user_id')
                if not cookie:
                    cookie = uuid.uuid4().hex
                    anon_cookie_to_set = cookie
            else:
                cookie = None

            order = Order.objects.create(
                solicitant_name="",
                solicitant_contact="",
                solicitant_address="",
                order_identified=None,
                anonymous_user_cookie=(cookie if not (hasattr(request, 'user') and request.user.is_authenticated) else None),
                registered_user=(request.user if hasattr(request, 'user') and request.user.is_authenticated else None),
                is_paid=False,
                status='EN_CARRITO',
            )


        try:
            requested_quantity = int(requested_quantity)
        except (TypeError, ValueError):
            requested_quantity = 1

        if requested_quantity < 1:
            requested_quantity = 1

        line = OrderProduct.objects.filter(order=order, product=product).first()
        if line:

            max_addable = max(product.stock - line.quantity, 0)
            to_add = min(requested_quantity, max_addable)
            if to_add > 0:
                line.quantity += to_add
                line.save()
        else:
            to_add = min(requested_quantity, max(product.stock, 0))
            if to_add > 0:
                line = OrderProduct.objects.create(order=order, product=product, quantity=to_add, price_at_order=product.price)
            else:
                line = None

        return line, anon_cookie_to_set
    def get_cart_order(solicitant_name, solicitant_contact):
        """Devuelve el QuerySet de `Order` en estado 'EN_CARRITO' para solicitante."""
        return Order.objects.filter(status='EN_CARRITO', solicitant_name=solicitant_name, solicitant_contact=solicitant_contact)

    @transaction.atomic
    def update_order_status(order_id, new_status):    
        """Actualiza el `status` de un `Order` o (si se pasa id de línea) del `Order` asociado."""
        order = Order.objects.filter(id=order_id).first()
        if order:
            order.status = new_status
            order.save()
            return order

        line = OrderProduct.objects.filter(id=order_id).first()
        if line:
            line.order.status = new_status
            line.order.save()
            return line.order

        raise Order.DoesNotExist(f"No Order or OrderProduct found with id={order_id}")

    @transaction.atomic
    def mark_order_as_paid(order_id):
        """Marca como pagado un `Order` (o el `Order` asociado a una línea)."""
        order = Order.objects.filter(id=order_id).first()
        if not order:
            line = OrderProduct.objects.filter(id=order_id).first()
            if not line:
                raise Order.DoesNotExist(f"No Order or OrderProduct found with id={order_id}")
            order = line.order
        if order.is_paid:
            return order

        if not order.order_identified:
            for _ in range(10):
                candidate = f"ORD-{uuid.uuid4().hex[:12].upper()}"
                if not Order.objects.filter(order_identified=candidate).exists():
                    order.order_identified = candidate
                    break
            else:
                order.order_identified = f"ORD-{int(datetime.datetime.utcnow().timestamp())}-{uuid.uuid4().hex[:6].upper()}"
        lines = OrderProduct.objects.filter(order=order)
        for l in lines:
            prod = l.product
            try:
                qty = int(l.quantity or 0)
            except (TypeError, ValueError):
                qty = 0
            if qty > 0:
                new_stock = (prod.stock or 0) - qty
                if new_stock < 0:
                    new_stock = 0
                prod.stock = new_stock
                prod.save()

        order.is_paid = True
        order.save()
        return order

    @transaction.atomic
    def remove_product_from_cart(order_id):
        """Remueve o decrementa la cantidad de una línea (`OrderProduct`).

        - Si `solicitation_id` corresponde a un `OrderProduct`, actúa sobre él.
        - Si corresponde a un `Order`, borra el pedido entero (solo si está en carrito).
        """
        line = OrderProduct.objects.filter(id=order_id).first()
        if line and line.order.status == 'EN_CARRITO':
            if line.quantity <= 1:
                line.delete()
                return True
            else:
                line.quantity -= 1
                line.save()
                return line


        order = Order.objects.filter(id=order_id).first()
        if order and order.status == 'EN_CARRITO':
            order.delete()
            return True

        return False

    def find_order_by_identifier(order_identified):
        order = Order.objects.filter(order_identified=order_identified).first()
        if order:
            return order

