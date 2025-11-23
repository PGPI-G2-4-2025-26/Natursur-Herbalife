from django.core.management.base import BaseCommand
from decimal import Decimal



DEFAULT_APPOINTMENTS = [
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

DEFAULT_USERS = [
    {
        'username': 'admin',
        'email': 'admin@example.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'password': 'adminpass',
        'is_staff': True,
        'is_superuser': False,
    },
    {
        'username': 'superadmin',
        'email': 'superadmin@example.com',
        'first_name': 'Super',
        'last_name': 'Admin',
        'password': 'superadminpass',
        'is_staff': True,
        'is_superuser': True,
    },
    {    'username': 'client',
        'email': 'client@example.com',
        'first_name': 'Client',
        'last_name': 'User',
        'password': 'clientpass',
        'is_staff': False,
        'is_superuser': False,
    },
]

DEFAULT_PRODUCTS = [
    {
        'name': "Product A",
        'ref': "PROD-A",
        'price': Decimal('19.99'),
        'flavor': "Vanilla",
        'size': "Medium",
    },
    {
        'name': "Product B",
        'ref': "PROD-B",
        'price': Decimal('29.99'),
        'flavor': "Chocolate",
        'size': "Large",
    }
]

DEFAULT_ORDERS = [
    {
        'id': 1,
        'total_price': Decimal('49.98'),
        'is_paid': True,
        'date': None,
        'status': 'SOLICITADO',
        'user_id': 3,  # Assuming user with ID 3 exists
        'telephone': '123456789',
        'full_name': 'Client User',
        'contact_email': 'client@example.com',
    },
    {
        'id': 2,
        'total_price': Decimal('29.99'),
        'is_paid': False,
        'date': None,
        'status': 'ENCARGADO',
        'user_id': 3,  # Assuming user with ID 3 exists
        'telephone': '123456789',
        'full_name': 'Client User',
        'contact_email': 'client@example.com',
    },
    {
        'id': 3,
        'total_price': Decimal('19.99'),
        'is_paid': True,
        'date': None,
        'status': 'RECOGIDO_CLIENTE',
        'user_id': 2,  # Assuming user with ID 2 exists
        'telephone': '987654321',
        'full_name': 'Super Admin',
        'contact_email': 'superadmin@example.com',
    },
    {
        'id': 4,
        'total_price': Decimal('0.00'),
        'is_paid': False,
        'date': None,
        'status': 'EN_CARRITO',
        'user_id': 3,  # Assuming user with ID 3 exists
        'telephone': '123456789',
        'full_name': 'Client User',
        'contact_email': 'client@example.com',
    },
    {
        'id': 5,
        'total_price': Decimal('99.99'),
        'is_paid': False,
        'date': None,
        'status': 'SOLICITADO',
        'user_id': 3,
        'telephone': '123456789',
        'full_name': 'Client User',
        'contact_email': 'client@example.com',
    },
    {
        'id': 6,
        'total_price': Decimal('59.99'),
        'is_paid': True,
        'date': None,
        'status': 'RECOGIDO_CLIENTE',
        'user_id': 3,
        'telephone': '987654321',
        'full_name': 'Super Admin',
        'contact_email': 'superadmin@example.com',
    },
    {
        'id': 7,
        'total_price': Decimal('39.99'),
        'is_paid': False,
        'date': None,
        'status': 'SOLICITADO',
        'user_id': 3,
        'telephone': '123456789',
        'full_name': 'Client User',
        'contact_email': 'client@example.com',
    }
]

DEFAULT_ORDER_PRODUCTS = [
    {
        'product_id': 1,
        'quantity': 2,
        'order_id': 1,
    },
    {
        'product_id': 2,
        'quantity': 1,
        'order_id': 1,
    },
    {
        'product_id': 2,
        'quantity': 1,
        'order_id': 2,
    },
    {
        'product_id': 1,
        'quantity': 1,
        'order_id': 3,
    },
    {
        'product_id': 1,
        'quantity': 1,
        'order_id': 4,
    },
    {
        'product_id': 1,
        'quantity': 1,
        'order_id': 5,
    },
    {
        'product_id': 2,
        'quantity': 3,
        'order_id': 6,
    },
    {
        'product_id': 1,
        'quantity': 2,
        'order_id': 7,
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

        for p in DEFAULT_PRODUCTS:
            obj, created = Product.objects.update_or_create(
                ref=p['ref'],
                defaults={
                    'name': p['name'],
                    'price': p['price'],
                    'flavor': p['flavor'],
                    'size': p['size'],
                }
            )
            if created:
                created_cnt += 1
                self.stdout.write(self.style.SUCCESS(f"Created product: {obj.name}"))
            else:
                updated_cnt += 1
                self.stdout.write(self.style.NOTICE(f"Updated product: {obj.name}"))
        
        for o in DEFAULT_ORDERS:
            obj, created = Order.objects.update_or_create(
                id=o['id'],
                defaults={
                    'total_price': o['total_price'],
                    'status': o['status'],
                    'user_id': o['user_id'],
                    'telephone': o['telephone'],
                    'full_name': o['full_name'],
                    'contact_email': o['contact_email'],
                }
            )
            if created:
                created_cnt += 1
                self.stdout.write(self.style.SUCCESS(f"Created order: {obj.id}"))
            else:
                updated_cnt += 1
                self.stdout.write(self.style.NOTICE(f"Updated order: {obj.id}"))
        
        for op in DEFAULT_ORDER_PRODUCTS:
            obj, created = OrderProduct.objects.update_or_create(
                id=op.get('id'),
                defaults={
                    'product_id': op['product_id'],
                    'quantity': op['quantity'],
                    'order_id': op['order_id'],
                }
            )
            if created:
                created_cnt += 1
                self.stdout.write(self.style.SUCCESS(f"Created ordered product: {obj.id}"))
            else:
                updated_cnt += 1
                self.stdout.write(self.style.NOTICE(f"Updated ordered product: {obj.id}"))

        self.stdout.write(self.style.SUCCESS(f"Seeding finished. Created: {created_cnt}, Updated: {updated_cnt}"))
