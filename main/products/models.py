from django.db import models



class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Name")
    ref = models.CharField(max_length=100, blank=True, null=True, verbose_name="Reference/SKU")
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

