from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from numpy import prod

from main.orders.models import Order, OrderProduct
from main.products.models import Product
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from main.orders.models import Order
from decimal import Decimal


class ProductViewsTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(username='user', password='pass')
		self.staff = User.objects.create_user(username='staff', password='pass', is_staff=True)
		self.p1 = Product.objects.create(name='Apple', price=10.00, stock=5)
		self.p2 = Product.objects.create(name='Banana', price=5.00, stock=0)
		self.p3 = Product.objects.create(name='Apricot', price=7.50, stock=3)

	def test_user_is_admin_function(self):
		from main.products.views import is_admin
		self.assertFalse(is_admin(self.user))
		self.assertTrue(is_admin(self.staff))
		
	def test_list_products_no_cart(self):
		url = reverse('list_products')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)

		self.assertIn('q', resp.context)
		self.assertEqual(resp.context['q'], '')
		products_page = resp.context['products']

		found = {p.name: p for p in products_page}
		self.assertIn('Apple', found)
		apple = found['Apple']
		self.assertEqual(getattr(apple, 'in_cart_qty', 0), 0)
		self.assertEqual(getattr(apple, 'available_stock', None), apple.stock)
		self.assertEqual(getattr(apple, 'max_add', None), apple.stock)

	def test_list_products_with_cart_for_user(self):

		order = Order.objects.create(status='EN_CARRITO', registered_user=self.user)
		OrderProduct.objects.create(order=order, product=self.p1, quantity=2, price_at_order=self.p1.price)

		self.client.login(username='user', password='pass')
		url = reverse('list_products')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		products_page = resp.context['products']
		found = {p.name: p for p in products_page}
		apple = found['Apple']
		self.assertEqual(apple.in_cart_qty, 2)
		self.assertEqual(apple.available_stock, max(apple.stock - 2, 0))
		self.assertEqual(apple.max_add, max(apple.stock - 2, 0))

	def test_search_query_filters(self):
		url = reverse('list_products') + '?q=ap'
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		products_page = resp.context['products']
		names = [p.name for p in products_page]

		self.assertIn('Apple', names)
		self.assertIn('Apricot', names)
		self.assertNotIn('Banana', names)

	def test_show_product_admin_requires_staff(self):
		url = reverse('show_products_admin')
	
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 302)
	
	
		self.client.login(username='user', password='pass')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 302)
	
	
		self.client.login(username='staff', password='pass')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
	
	def test_show_product_admin_search(self):
		self.client.login(username='staff', password='pass')
		url = reverse('show_products_admin') + '?q=ap'
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		products_page = resp.context['products']
		names = [p.name for p in products_page]

		self.assertIn('Apple', names)
		self.assertIn('Apricot', names)
		self.assertNotIn('Banana', names)

	def test_create_product_admin_no_post(self):
		self.client.login(username='staff', password='pass')
		url = reverse('create_product_admin')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
	
	def test_create_product_admin_post(self):
		self.client.login(username='staff', password='pass')
		url = reverse('create_product_admin')
		data = {'name': 'Orange', 'price': '4.00', 'stock': '10'}
		resp = self.client.post(url, data, follow=True)
		self.assertEqual(resp.status_code, 200)
		orange = Product.objects.filter(name='Orange').first()
		self.assertIsNotNone(orange)

	def test_edit_product_admin_invalid_id(self):
		self.client.login(username='staff', password='pass')
		url = reverse('edit_product_admin', args=[9999])
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 404)

	def test_edit_product_admin_no_post(self):
		self.client.login(username='staff', password='pass')
		url = reverse('edit_product_admin', args=[self.p1.id])
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
	
	def test_edit_product_admin_post(self):
		self.client.login(username='staff', password='pass')
		url = reverse('edit_product_admin', args=[self.p1.id])
		data = {'name': 'Green Apple', 'price': '12.00', 'stock': '7'}
		resp = self.client.post(url, data, follow=True)
		self.assertEqual(resp.status_code, 200)
		self.p1.refresh_from_db()
		self.assertEqual(self.p1.name, 'Green Apple')
		self.assertEqual(str(self.p1.price), '12.00')
		self.assertEqual(self.p1.stock, 7)

	def test_delete_product_admin_get_redirect(self):
		self.client.login(username='staff', password='pass')
		url = reverse('delete_product_admin', args=[self.p1.id])
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 302)
		self.assertTrue(Product.objects.filter(id=self.p1.id).exists())

	def test_delete_product_admin_requires_staff(self):
		url = reverse('delete_product_admin', args=[self.p1.id])
		resp = self.client.post(url)
		self.assertEqual(resp.status_code, 302)
		self.assertTrue(Product.objects.filter(id=self.p1.id).exists())

		self.client.login(username='user', password='pass')
		resp = self.client.post(url)
		self.assertEqual(resp.status_code, 302)
		self.assertTrue(Product.objects.filter(id=self.p1.id).exists())

	def test_delete_product_admin_invalid_id_returns_404(self):
		self.client.login(username='staff', password='pass')
		url = reverse('delete_product_admin', args=[999999])
		resp = self.client.post(url)
		self.assertEqual(resp.status_code, 404)

	def test_delete_product_admin_post_deletes_cart_and_snapshots_history(self):
		p = Product.objects.create(name='ToDelete', price=2.50, stock=5)
		img = SimpleUploadedFile('img.jpg', b'content', content_type='image/jpeg')
		p.image.save('img.jpg', img)
		p.save()

		cart = Order.objects.create(status='EN_CARRITO', registered_user=self.user)
		hist = Order.objects.create(status='SOLICITADO', registered_user=self.user)

		OrderProduct.objects.create(order=cart, product=p, quantity=2, price_at_order=p.price)

		inst = OrderProduct(order=hist, product=p, quantity=1)
		OrderProduct.objects.bulk_create([inst])
		h_line = OrderProduct.objects.filter(order=hist, product=p).first()

		expected_image = getattr(p.image, 'url', None) or getattr(p.image, 'name', None)

		self.client.login(username='staff', password='pass')
		url = reverse('delete_product_admin', args=[p.id])
		resp = self.client.post(url, follow=True)
		self.assertEqual(resp.status_code, 200)

		self.assertFalse(Product.objects.filter(id=p.id).exists())

		self.assertFalse(OrderProduct.objects.filter(order=cart).exists())

		h = OrderProduct.objects.get(id=h_line.id)
		self.assertIsNone(h.product)
		self.assertEqual(h.product_name, 'ToDelete')
		self.assertEqual(h.product_image, expected_image)
		p_price_dec = Decimal(str(p.price))
		self.assertEqual(h.price_at_order.quantize(Decimal('0.01')), p_price_dec.quantize(Decimal('0.01')))

	def test_delete_product_admin_preserves_existing_snapshots(self):
		p = Product.objects.create(name='KeepSnapshots', price=9.99, stock=2)

		hist = Order.objects.create(status='SOLICITADO', registered_user=self.user)
		old_name = 'OldName'
		old_image = 'some_img.png'
		old_price = Decimal('4.44')
		h_line = OrderProduct.objects.create(order=hist, product=p, quantity=1, product_name=old_name, product_image=old_image, price_at_order=old_price)

		self.client.login(username='staff', password='pass')
		url = reverse('delete_product_admin', args=[p.id])
		resp = self.client.post(url, follow=True)
		self.assertEqual(resp.status_code, 200)

		h = OrderProduct.objects.get(id=h_line.id)
		self.assertIsNone(h.product)
		self.assertEqual(h.product_name, old_name)
		self.assertEqual(h.product_image, old_image)
		self.assertEqual(h.price_at_order.quantize(Decimal('0.01')), old_price.quantize(Decimal('0.01')))
	
    