from django.core.management.base import BaseCommand
from decimal import Decimal


DEFAULT_SERVICES = [
    {
        'name': "Sesión 40'",
        'price': Decimal('28.00'),
        'duration': 40,
        'description': '',
        'premium': False,
        'discount': Decimal('0.00'),
        'endDiscount': None,
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


class Command(BaseCommand):
    help = 'Seed default services into Service model'

    def handle(self, *args, **options):
        from django.apps import apps

        # The app is registered in INSTALLED_APPS as 'main.service',
        # but the AppConfig.label for that package is 'service'.
        # Use that label when retrieving the model.
        Service = apps.get_model('service', 'Service')
        created_cnt = 0
        updated_cnt = 0

        for s in DEFAULT_SERVICES:
            obj, created = Service.objects.update_or_create(
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
                self.stdout.write(self.style.SUCCESS(f"Created service: {obj.name}"))
            else:
                updated_cnt += 1
                self.stdout.write(self.style.NOTICE(f"Updated service: {obj.name}"))

        self.stdout.write(self.style.SUCCESS(f"Seeding finished. Created: {created_cnt}, Updated: {updated_cnt}"))
