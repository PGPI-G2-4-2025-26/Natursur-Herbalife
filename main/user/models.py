import os
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

def profile_photo_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{instance.user.username}Photo.{ext}"
    return os.path.join('user_photos', new_filename)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone")
    photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True, verbose_name="Photo")    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"Profile for {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)