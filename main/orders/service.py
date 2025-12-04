from ..products.models import Product
from main.orders.models import Order, OrderProduct
import datetime
from django.db import transaction
import uuid
from django.core.exceptions import ValidationError


class InsufficientStockError(Exception):
    """Excepción lanzada cuando faltan unidades de uno o varios productos.

    Se usa en vez de `ValidationError` para preservar la estructura de datos
    (lista de diccionarios) en el atributo `removed`.
    """
    def __init__(self, removed):
        super().__init__("insufficient_stock")
        self.removed = removed


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
        
    @staticmethod
    def get_active_cart_for_request(request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            return Order.objects.filter(status='EN_CARRITO', registered_user=request.user).first()
        else:
            cookie = request.COOKIES.get('anon_user_id')
            if cookie:
                return Order.objects.filter(status='EN_CARRITO', anonymous_user_cookie=cookie).first()
        return None

