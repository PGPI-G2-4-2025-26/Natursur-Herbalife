from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Name")
    ref = models.CharField(max_length=50, verbose_name="Reference/SKU")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Price")
    flavor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Flavor")
    size = models.CharField(max_length=100, blank=True, null=True, verbose_name="Size")
    image = models.ImageField(upload_to='products', blank=True, null=True)
    stock = models.PositiveIntegerField(default=10, verbose_name="Stock Quantity")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def _str_(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('EN_CARRITO', _('IN CART')),
        ('SOLICITADO', _('SOLICITED')),
        ('ENCARGADO', _('ORDERED')),
        ('RECIBIDO_NATURSUR', _('RECEIVED BY NATURSUR')),
        ('RECOGIDO_CLIENTE', _('PICKED UP BY CLIENT')),
    ]

    products = models.ManyToManyField('Product', through='OrderProduct', related_name='orders', verbose_name="Ordered Products (productos_solicitados)")

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
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Product (id_producto)')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    price_at_order = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Price at order')

    class Meta:
        verbose_name = "Ordered Product"
        verbose_name_plural = "Ordered Products"

    def _str_(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"