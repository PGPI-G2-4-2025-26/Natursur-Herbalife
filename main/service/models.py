from django.db import models



class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Price")
    duration = models.PositiveIntegerField(verbose_name="Duration (minutes)")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    premium = models.BooleanField(default=False, verbose_name="Premium")
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Discount")
    endDiscount = models.DateField(blank=True, null=True, verbose_name="End Discount Date")

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.name