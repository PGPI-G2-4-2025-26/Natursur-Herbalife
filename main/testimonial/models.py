from django.db import models
from django.utils.translation import gettext_lazy as _

class Testimonial(models.Model):
    author = models.CharField(max_length=500, verbose_name="Author")
    text = models.TextField(verbose_name="Testimonial Text")
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True, verbose_name="Client Photo")
    date_published = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"Testimonial from {self.client_name}"