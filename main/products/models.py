from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Name")
    ref = models.CharField(max_length=50, unique=True, verbose_name="Reference/SKU")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Price")
    flavor = models.CharField(max_length=100, blank=True, null=True, verbose_name="Flavor")
    size = models.CharField(max_length=100, blank=True, null=True, verbose_name="Size")
    image = models.ImageField(upload_to='products', blank=True, null=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name
    

class Order(models.Model):

    STATUS_CHOICES = [
        ('EN_CARRITO', _('IN CART')),
        ('SOLICITADO', _('SOLICITED')),
        ('ENCARGADO', _('ORDERED')),
        ('RECIBIDO_NATURSUR', _('RECEIVED BY NATURSUR')),
        ('RECOGIDO_CLIENTE', _('PICKED UP BY CLIENT')),
    ]

    total_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Total Price")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SOLICITADO', verbose_name="Status (estado)")
    telephone = models.CharField(max_length=20, verbose_name="Telephone")
    full_name = models.CharField(max_length=40, verbose_name="Full Name")
    contact_email = models.EmailField(verbose_name="Contact Email")
    notas = models.TextField(max_length=255, blank=True, null=True, verbose_name="Notes")
    
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="User"
    )
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order #{self.id} - Total: {self.total_price}"

    
class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Product (id_producto)")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Order")
    class Meta:
        verbose_name = "Order Product"
        verbose_name_plural = "Order Products"    

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class ProductSolicitation(models.Model):
    
    STATUS_CHOICES = [
        ('EN_CARRITO', _('IN CART')),
        ('SOLICITADO', _('SOLICITED')),
        ('ENCARGADO', _('ORDERED')),
        ('RECIBIDO_NATURSUR', _('RECEIVED BY NATURSUR')),
        ('RECOGIDO_CLIENTE', _('PICKED UP BY CLIENT')),
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Product (id_producto)")

    solicitant_name = models.CharField(max_length=255, verbose_name="Solicitant Full Name (String)")
    solicitant_contact = models.CharField(max_length=255, verbose_name="Solicitant Contact (Email/Phone)")

    registered_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Linked Registered User"
    )

    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    is_paid = models.BooleanField(default=False, verbose_name="Is Paid (estaPagado)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SOLICITADO', verbose_name="Status (estado)")

    class Meta:
        verbose_name = "Solicited Product"
        verbose_name_plural = "Solicited Products"

    def __str__(self):
        return f"{self.quantity} x {self.product.name} - Status: {self.get_status_display()}"