from django.core.management.base import BaseCommand
from decimal import Decimal
import os
import shutil
from django.conf import settings
from main.user.models import UserProfile
from datetime import datetime


DEFAULT_APPOINTMENTS = [
    {
        'name': "Sesión 40'",
        'price': Decimal('28.00'),
        'duration': 40,
        'description': '',
        'premium': False,
        'discount': Decimal('15.00'),
        'endDiscount': datetime(2025, 12, 31, 23, 59),
    },
    {
        'name': "Sesión 60'",
        'price': Decimal('45.00'),
        'duration': 60,
        'description': '',
        'premium': False,
        'discount': Decimal('0.00'),
        'endDiscount': None,
    },
    {
        'name': "Sesión 90'",
        'price': Decimal('70.00'),
        'duration': 90,
        'description': '',
        'premium': False,
        'discount': Decimal('0.00'),
        'endDiscount': None,
    },
    {
        'name': "3 sesiones de 40'",
        'price': Decimal('70.00'),
        'duration': 40,
        'description': '',
        'premium': False,
        'discount': Decimal('0.00'),
        'endDiscount': None,
    },
    {
        'name': "Sesión Premium 60'",
        'price': Decimal('50.00'),
        'duration': 60,
        'description': 'Masaje, osteopatía, par biomagnético y emociones atrapadas.',
        'premium': True,
        'discount': Decimal('0.00'),
        'endDiscount': None,
    },
    {
        'name': "Domicilio 60'",
        'price': Decimal('100.00'),
        'duration': 60,
        'description': '',
        'premium': False,
        'discount': Decimal('0.00'),
        'endDiscount': None,
    },
]

DEFAULT_USERS = [
    {
        'username': 'admin',
        'email': 'admin@example.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'password': 'adminpass',
        'is_staff': True,
        'is_superuser': False,
        'phone': '666111222',
        'photo': 'adminPhoto.png',
        

    },
    {
        'username': 'superadmin',
        'email': 'superadmin@example.com',
        'first_name': 'Super',
        'last_name': 'Admin',
        'password': 'superadminpass',
        'is_staff': True,
        'is_superuser': True,
        'phone': '666777000',
    },
    {    'username': 'client',
        'email': 'client@example.com',
        'first_name': 'Client',
        'last_name': 'User',
        'password': 'clientpass',
        'is_staff': False,
        'is_superuser': False,
        'phone': '666555444',
        'photo': 'clientPhoto.png',
    },
]

class Command(BaseCommand):
    help = 'Seed default appointments into Appointment model'

    def handle(self, *args, **options):
        from django.apps import apps

        Appointment = apps.get_model('appointments', 'Appointment')
        User = apps.get_model('auth', 'User')
        Product = apps.get_model('products', 'Product')
        Order = apps.get_model('products', 'Order')
        OrderProduct = apps.get_model('products', 'OrderProduct')

        created_cnt = 0
        updated_cnt = 0

        for u in DEFAULT_USERS:
            obj, created = User.objects.update_or_create(
                username=u['username'],
                defaults={
                    'email': u['email'],
                    'first_name': u['first_name'],
                    'last_name': u['last_name'],
                    'is_staff': u['is_staff'],
                    'is_superuser': u['is_superuser'],
                }
            )
            if created:
                obj.set_password(u['password'])
                obj.save()
                created_cnt += 1
                self.stdout.write(self.style.SUCCESS(f"Created user: {obj.username}"))
            else:
                updated_cnt += 1
                self.stdout.write(self.style.NOTICE(f"Updated user: {obj.username}"))


        for u in DEFAULT_USERS:
            user = User.objects.get(username=u['username'])
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone = u.get('phone', '')
            if u.get('photo'):
                filename = u.get('photo')
                source_path = os.path.join(settings.BASE_DIR, 'seed_data', 'photos', filename)
                source_path = os.path.join(settings.BASE_DIR, 'seed_data', 'photos', filename)
                destination_dir = os.path.join(settings.MEDIA_ROOT, 'user_photos')
                destination_path = os.path.join(destination_dir, filename)
                
                if os.path.exists(source_path):
                    os.makedirs(destination_dir, exist_ok=True)
                    shutil.copy(source_path, destination_path)
                    profile.photo = f'user_photos/{filename}'
                else:
                    self.stdout.write(self.style.WARNING(f"FOTO NO ENCONTRADA: {source_path}"))
            
            profile.save()

            if created:
                created_cnt += 1
                self.stdout.write(self.style.SUCCESS(f"Created profile for user: {user.username}"))
            else:
                updated_cnt += 1
                self.stdout.write(self.style.NOTICE(f"Updated profile for user: {user.username}"))

        for s in DEFAULT_APPOINTMENTS:
            obj, created = Appointment.objects.update_or_create(
                name=s['name'],
                defaults={
                    'price': s['price'],
                    'duration': s['duration'],
                    'description': s['description'],
                    'premium': s['premium'],
                    'discount': s['discount'],
                }
            )
            if created:
                created_cnt += 1
                self.stdout.write(self.style.SUCCESS(f"Created appointment: {obj.name}"))
            else:
                updated_cnt += 1
                self.stdout.write(self.style.NOTICE(f"Updated appointment: {obj.name}"))

        self.stdout.write(self.style.SUCCESS(f"Seeding finished. Created: {created_cnt}, Updated: {updated_cnt}"))
