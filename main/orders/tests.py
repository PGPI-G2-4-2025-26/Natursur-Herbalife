from decimal import Decimal
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.orders import views as order_views
from main.orders.service import ProductService

from main.orders.models import Order, OrderProduct
from main.products.models import Product


class OrderViewsTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='user', password='pass')
        self.staff = User.objects.create_user(username='staff', password='pass', is_staff=True)
        self.p1 = Product.objects.create(name='Prod1', price=Decimal('1.50'), stock=5)
        self.p2 = Product.objects.create(name='Prod2', price=Decimal('2.00'), stock=0)
        self.factory = RequestFactory()

    def test_user_is_admin_function(self):
        from main.products.views import is_admin
        self.assertFalse(is_admin(self.user))
        self.assertTrue(is_admin(self.staff))
    
    def test__format_price_with_none(self):
        disp = order_views._format_price('20,0')
        self.assertIsInstance(disp, str)
        self.assertIn(',', disp)

    def test__format_price_and_prepare_order_lines_with_various_prices(self):
        order = Order.objects.create(status='EN_CARRITO', registered_user=self.user)
        OrderProduct.objects.create(order=order, product=self.p1, quantity=2, price_at_order=Decimal('1.50'))

        OrderProduct.objects.create(order=order, product=self.p2, quantity=3, price_at_order=None)

        items, total = order_views._prepare_order_lines(order)
        self.assertEqual(len(items), 2)
        self.assertIsInstance(total, Decimal)
        disp = order_views._format_price(total)
        self.assertIsInstance(disp, str)

    def test_list_user_cart_order_cookie_and_authenticated(self):
        # anonymous cookie
        req = self.factory.get('/')
        cookie_order = Order.objects.create(status='EN_CARRITO', anonymous_user_cookie='abc123')
        req.COOKIES['anon_user_id'] = 'abc123'
        # attach a user to request and test
        req.user = type('U', (), {'is_authenticated': False})()
        found = order_views.list_user_cart_order(req)
        self.assertIsNotNone(found)

        # authenticated user
        req2 = self.factory.get('/')
        req2.user = self.user
        auth_order = Order.objects.create(status='EN_CARRITO', registered_user=self.user)
        found2 = order_views.list_user_cart_order(req2)
        self.assertIsNotNone(found2)

    def test_view_cart(self):
        # view_cart without order
        req = self.factory.get('/')
        req.user = self.user
        resp = order_views.view_cart(req)
        self.assertEqual(resp.status_code, 200)

        #view_cart with order
        order = Order.objects.create(status='EN_CARRITO', registered_user=self.user)
        OrderProduct.objects.create(order=order, product=self.p1, quantity=1, price_at_order=self.p1.price)
        req2 = self.factory.get('/')
        req2.user = self.user
        resp2 = order_views.view_cart(req2)
        self.assertEqual(resp2.status_code, 200)

    def test_remove_from_cart_redirects(self):

        # remove_from_cart GET should redirect
        req = self.factory.get('/')
        req.user = self.user
        resp = order_views.remove_from_cart(req, item_id=1)
        self.assertEqual(resp.status_code, 302)

        # remove_from_cart no POST should redirect
        req2 = self.factory.post('/')
        req2.user = self.user
        resp2 = order_views.remove_from_cart(req2, item_id=1)
        self.assertEqual(resp2.status_code, 302)


    def test_add_to_cart_invalid_method_and_messages_and_cookie(self):
        # GET should redirect
        req = self.factory.get('/')
        req.user = self.user
        resp = order_views.add_to_cart(req, product_id=self.p1.id)
        self.assertEqual(resp.status_code, 302)

        # POST with invalid quantity should default to 1
        req = self.factory.post('/', {'quantity': 'bad', 'page': '1'})
        req.user = self.user
        # need cookies and session to use messages; use client instead for full flow
        self.client.login(username='user', password='pass')
        resp = self.client.post(reverse('add_to_cart', args=[self.p1.id]), {'quantity': 'bad', 'page': '1'}, follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_add_to_cart_negative_quantity_creates_one(self):
        # POST with negative quantity should be normalized to 1 and create a line with quantity 1
        resp = self.client.post(reverse('add_to_cart', args=[self.p1.id]), {'quantity': '-5', 'page': '1'}, follow=True)
        self.assertEqual(resp.status_code, 200)

        # an order in cart should exist (anonymous or user)
        order = Order.objects.filter(status='EN_CARRITO').first()
        self.assertIsNotNone(order)

        line = OrderProduct.objects.filter(order=order, product=self.p1).first()
        self.assertIsNotNone(line)
        self.assertEqual(line.quantity, 1)

    def test_finalize_order(self):
        # create order and finalize
        order = Order.objects.create(status='EN_CARRITO', registered_user=self.user)
        OrderProduct.objects.create(order=order, product=self.p1, quantity=1, price_at_order=self.p1.price)

        self.client.login(username='user', password='pass')
        resp = self.client.post(reverse('finalize_order'), {
            'solicitant_name': 'Test User',
            'solicitant_contact': 'test@example.com',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)

        # refresh order from db and check status changed
        order.refresh_from_db()
        self.assertEqual(order.status, 'SOLICITADO')

    def test_finalize_invalid_form(self):
        # create order and finalize
        order = Order.objects.create(status='EN_CARRITO', registered_user=self.user)
        OrderProduct.objects.create(order=order, product=self.p1, quantity=1, price_at_order=self.p1.price)

        self.client.login(username='user', password='pass')
        resp = self.client.post(reverse('finalize_order'), {
            'solicitant_name': '',
            'solicitant_contact': '',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)

        # refresh order from db and check status changed
        order.refresh_from_db()
        self.assertEqual(order.status, 'EN_CARRITO')

    def test_finalize_order_no_order_and_finalize_flow_errors(self):
        # finalize without cart should redirect with message
        self.client.login(username='user', password='pass')
        resp = self.client.post(reverse('finalize_order'), follow=True)
        self.assertEqual(resp.status_code, 200)

        # create order and finalize with invalid form data (POST) to force re-render
        order = Order.objects.create(status='EN_CARRITO', registered_user=self.user)
        OrderProduct.objects.create(order=order, product=self.p1, quantity=1, price_at_order=self.p1.price)
        resp = self.client.get(reverse('finalize_order'))
        self.assertEqual(resp.status_code, 200)

    def test_finalize_order_no_stock(self):
        # create order with out-of-stock product
        order = Order.objects.create(status='EN_CARRITO', registered_user=self.user)
        OrderProduct.objects.create(order=order, product=self.p2, quantity=1, price_at_order=self.p2.price)

        self.client.login(username='user', password='pass')
        resp = self.client.post(reverse('finalize_order'), {
            'solicitant_name': 'Test User',
            'solicitant_contact': 'test@example.com',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
    
    def test_finalize_order_with_identified(self):
        # create order and finalize with identified order
        order = Order.objects.create(status='EN_CARRITO', registered_user=self.user)
        OrderProduct.objects.create(order=order, product=self.p1, quantity=1, price_at_order=self.p1.price)

        self.client.login(username='user', password='pass')
        resp = self.client.post(reverse('finalize_order'), {
            'solicitant_name': 'Test User',
            'solicitant_contact': 'test@example.com',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_show_orders_pagination_and_per_page_validation(self):
        # create multiple orders
        for i in range(7):
            Order.objects.create(status='SOLICITADO', registered_user=self.user)
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('show_orders'))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(reverse('show_orders') + '?per_page=999')
        self.assertEqual(resp.status_code, 200)

    def test_show_orders_admin_filters_and_admin_access(self):
        for i in range(3):
            Order.objects.create(status='SOLICITADO', registered_user=self.user)
        # non-logged -> redirect
        resp = self.client.get(reverse('show_orders_admin'))
        self.assertEqual(resp.status_code, 302)
        # as staff
        self.client.login(username='staff', password='pass')
        resp = self.client.get(reverse('show_orders_admin'))
        self.assertEqual(resp.status_code, 200)

    def test_edit_and_delete_order_admin(self):
        o = Order.objects.create(status='SOLICITADO', registered_user=self.user)
        self.client.login(username='staff', password='pass')
        # edit status via POST
        resp = self.client.post(reverse('edit_order', args=[o.id]), {'status': 'RECIBIDO_NATURSUR'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        # delete
        resp = self.client.post(reverse('delete_order', args=[o.id]), follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_order_detail_access_control(self):
        o = Order.objects.create(status='SOLICITADO', registered_user=self.user)
        # anonymous cannot access
        resp = self.client.get(reverse('order_detail', args=[o.id]))
        self.assertEqual(resp.status_code, 302)
        # login user
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('order_detail', args=[o.id]))
        self.assertEqual(resp.status_code, 200)
        # staff can access any
        self.client.login(username='staff', password='pass')
        resp = self.client.get(reverse('order_detail', args=[o.id]))
        self.assertEqual(resp.status_code, 200)

    def test_show_orders_filters_and_pagination(self):
        # Crear órdenes con diferentes estados
        Order.objects.create(status='SOLICITADO', registered_user=self.user, solicitant_name='Order1')
        Order.objects.create(status='RECIBIDO_NATURSUR', registered_user=self.user, solicitant_name='Order2')
        Order.objects.create(status='ENVIADO', registered_user=self.user, solicitant_name='Order3')
        
        self.client.login(username='user', password='pass')
        
        # Test filtrado por status
        resp = self.client.get(reverse('show_orders') + '?status=SOLICITADO')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('orders', resp.context)
        self.assertEqual(len(resp.context['orders']), 1)
        
        # Test paginación con página inválida
        resp = self.client.get(reverse('show_orders') + '?page=999')
        self.assertEqual(resp.status_code, 200)
        
        # Test per_page con valor inválido (causa excepción)
        resp = self.client.get(reverse('show_orders') + '?per_page=abc')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['current_per_page'], 10)

    def test_show_orders_admin_filters_and_pagination(self):
        # Crear órdenes con diferentes estados
        Order.objects.create(status='SOLICITADO', registered_user=self.user, solicitant_name='AdminOrder1')
        Order.objects.create(status='RECIBIDO_NATURSUR', registered_user=self.user, solicitant_name='AdminOrder2')
        Order.objects.create(status='ENVIADO', registered_user=self.user, solicitant_name='AdminOrder3')
        
        self.client.login(username='staff', password='pass')
        
        # Test filtrado por status
        resp = self.client.get(reverse('show_orders_admin') + '?status=SOLICITADO')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('orders', resp.context)
        self.assertEqual(len(resp.context['orders']), 1)
        
        # Test paginación con página inválida
        resp = self.client.get(reverse('show_orders_admin') + '?page=999')
        self.assertEqual(resp.status_code, 200)
        
        # Test per_page con valor inválido (causa excepción)
        resp = self.client.get(reverse('show_orders_admin') + '?per_page=xyz')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['current_per_page'], 10)

    def test_show_orders_admin_name_filter(self):
        # Crear órdenes con diferentes nombres
        Order.objects.create(status='SOLICITADO', registered_user=self.user, solicitant_name='Juan Pérez')        
        self.client.login(username='staff', password='pass')
        
        # Filtrar por "Juan" (debería encontrar 1)
        resp = self.client.get(reverse('show_orders_admin') + '?q=Juan')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('orders', resp.context)
        self.assertEqual(len(resp.context['orders']), 1)

    def test_add_product_to_existing_line_updates_quantity(self):
        req = self.factory.post('/')
        req.user = self.user
        
        line, _ = ProductService.add_product_to_cart(req, {
            'id': self.p1.id,
            'name': self.p1.name,
            'ref': self.p1.ref,
            'price': self.p1.price,
        }, requested_quantity=2)
        self.assertEqual(line.quantity, 2)
        
        line, _ = ProductService.add_product_to_cart(req, {
            'id': self.p1.id,
            'name': self.p1.name,
            'ref': self.p1.ref,
            'price': self.p1.price,
        }, requested_quantity=3)
        line.refresh_from_db()
        self.assertEqual(line.quantity, 5)
        
        line, _ = ProductService.add_product_to_cart(req, {
            'id': self.p1.id,
            'name': self.p1.name,
            'ref': self.p1.ref,
            'price': self.p1.price,
        }, requested_quantity=10)
        line.refresh_from_db()
        self.assertEqual(line.quantity, 5)
        

    def test_remove_from_cart_item(self):
        order = Order.objects.create(status='EN_CARRITO', registered_user=self.user)
        
        line1 = OrderProduct.objects.create(order=order, product=self.p1, quantity=1, price_at_order=Decimal('1.50'))
        self.assertTrue(ProductService.remove_product_from_cart(line1.id))
        self.assertFalse(OrderProduct.objects.filter(id=line1.id).exists())
        
        line2 = OrderProduct.objects.create(order=order, product=self.p1, quantity=5, price_at_order=Decimal('1.50'))
        result = ProductService.remove_product_from_cart(line2.id)
        self.assertIsNotNone(result)
        line2.refresh_from_db()
        self.assertEqual(line2.quantity, 4)
        
        order2 = Order.objects.create(status='SOLICITADO', registered_user=self.user)
        line3 = OrderProduct.objects.create(order=order2, product=self.p1, quantity=1, price_at_order=Decimal('1.50'))
        self.assertFalse(ProductService.remove_product_from_cart(line3.id))
        self.assertTrue(OrderProduct.objects.filter(id=line3.id).exists())
        
        order3 = Order.objects.create(status='EN_CARRITO', registered_user=self.user)
        self.assertTrue(ProductService.remove_product_from_cart(order3.id))
        self.assertFalse(Order.objects.filter(id=order3.id).exists())
        
        self.assertFalse(ProductService.remove_product_from_cart(99999))
