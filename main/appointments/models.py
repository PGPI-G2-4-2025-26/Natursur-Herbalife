from django.db import models
from django.core.validators import MinValueValidator


class Appointment(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name")
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Price",
        validators=[MinValueValidator(0)],
    )
    duration = models.PositiveIntegerField(verbose_name="Duration (minutes)")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    premium = models.BooleanField(default=False, verbose_name="Premium")
    discount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Discount",
        validators=[MinValueValidator(0)],
    )
    endDiscount = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name="End Discount Date",
        db_column='endDiscount'
    )

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        db_table = 'main_appointment'

    def __str__(self):
        return self.name