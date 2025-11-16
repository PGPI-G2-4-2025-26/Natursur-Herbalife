from django.db import models
# Importamos el modelo User de Django para manejar el registro de usuarios y la relación solicitante
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone")
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True, verbose_name="Photo")
    
    # Si es Admin,  User.is_staff = True

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"Profile for {self.user.username}"

