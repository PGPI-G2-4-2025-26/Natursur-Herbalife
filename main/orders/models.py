from django.db import models
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from main.products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('EN_CARRITO', _('IN CART')),
        ('SOLICITADO', _('SOLICITED')),
        ('ENCARGADO', _('ORDERED')),
        ('RECIBIDO_NATURSUR', _('RECEIVED BY NATURSUR')),
        ('RECOGIDO_CLIENTE', _('PICKED UP BY CLIENT')),
    ]

    products = models.ManyToManyField(Product, through='OrderProduct', related_name='orders', verbose_name="Ordered Products (productos_solicitados)")

    solicitant_name = models.CharField(max_length=255, blank=True,null=True, default="", verbose_name="Solicitant Full Name (String)")
    solicitant_contact = models.CharField(max_length=255, blank=True,null=True, default="", verbose_name="Solicitant Contact (Email/Phone)")
    solicitant_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Solicitant Address (optional)")
    order_identified = models.CharField(max_length=100, blank=True, null=True, verbose_name="Order Identifier")
    
    anonymous_user_cookie = models.CharField(max_length=255, blank=True, null=True, verbose_name="Anonymous User Cookie")

    registered_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Linked Registered User"
    )

    date = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    is_paid = models.BooleanField(default=False, verbose_name="Is Paid (estaPagado)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SOLICITADO', verbose_name="Status (estado)")

    class Meta:
        verbose_name = "Solicited Product"
        verbose_name_plural = "Solicited Products"

    def _str_(self):
        return f"Order {self.id} - {self.get_status_display()}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name='order_products', on_delete=models.CASCADE, verbose_name='Order (id_pedido)')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Product (id_producto)')
    product_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='Product name (snapshot)')
    product_image = models.CharField(max_length=500, blank=True, null=True, verbose_name='Product image (snapshot)')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    price_at_order = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Price at order')

    class Meta:
        verbose_name = "Ordered Product"
        verbose_name_plural = "Ordered Products"

    def __str__(self):
        name = self.product_name or (self.product.name if self.product else '(producto eliminado)')
        return f"OrderProduct: {self.quantity} x {name} (Order {self.order.id})"

    def save(self, *args, **kwargs):
        if self.product:
            try:
                if not self.product_name:
                    self.product_name = self.product.name
            except Exception:
                pass
            try:
                if not self.product_image:
                    img = getattr(self.product, 'image', None)
                    if img:
                        try:
                            self.product_image = img.url
                        except Exception:
                            self.product_image = getattr(img, 'name', None)
            except Exception:
                pass
            try:
                if not self.price_at_order:
                    self.price_at_order = self.product.price
            except Exception:
                pass

        if not self.product and not self.product_name:
            self.product_name = '(producto eliminado)'

        super().save(*args, **kwargs)


@receiver(pre_delete, sender=Product)
def handle_product_pre_delete(sender, instance, **kwargs):

    try:
        cart_lines = OrderProduct.objects.filter(product=instance, order__status='EN_CARRITO')
        if cart_lines.exists():
            cart_lines.delete()

        hist_lines = OrderProduct.objects.filter(product=instance).exclude(order__status='EN_CARRITO')
        for l in hist_lines:
            changed = False
            if not getattr(l, 'product_name', None):
                l.product_name = instance.name
                changed = True
            if not getattr(l, 'product_image', None):
                img = getattr(instance, 'image', None)
                if img:
                    try:
                        l.product_image = img.url
                    except Exception:
                        l.product_image = getattr(img, 'name', None)
                    changed = True
            if not getattr(l, 'price_at_order', None):
                try:
                    l.price_at_order = instance.price
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
    except Exception:
        pass