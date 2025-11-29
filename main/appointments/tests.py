from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Appointment
from django.core.exceptions import ValidationError
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Appointment
from django.core.exceptions import ValidationError
from unittest.mock import patch


class CreateAppointmentViewTests(TestCase):
	def setUp(self):
		self.username = 'staffuser'
		self.password = 'pass1234'
		self.user = User.objects.create_user(username=self.username, password=self.password)
		self.user.is_staff = True
		self.user.save()

	def test_get_as_staff_renders_form(self):
		self.client.login(username=self.username, password=self.password)
		url = reverse('create_appointment')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertIn('form', response.context)

	def test_post_valid_creates_appointment_and_redirects(self):
		self.client.login(username=self.username, password=self.password)
		url = reverse('create_appointment')
		data = {
			'name': 'Sesión de prueba',
			'price': '25.00',
			'duration': '45',
			'description': 'Descripción de prueba',
			'premium': 'on',
		}
		response = self.client.post(url, data)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(Appointment.objects.filter(name='Sesión de prueba').count(), 1)

	def test_post_negative_price_shows_form_error(self):
		self.client.login(username=self.username, password=self.password)
		url = reverse('create_appointment')
		data = {
			'name': 'Sesión inválida',
			'price': '-5.00',
			'duration': '30',
			'description': 'Precio negativo',
		}
		response = self.client.post(url, data)
		self.assertEqual(response.status_code, 200)
		form = response.context.get('form')
		self.assertIsNotNone(form)
		self.assertTrue(form.errors)
		# price validation comes from model validators, so the error may be attached to 'price'
		self.assertIn('price', form.errors)
		self.assertEqual(Appointment.objects.filter(name='Sesión inválida').count(), 0)

	def test_post_full_clean_raises_non_field_messages_added(self):
		"""Forzar Appointment.full_clean() para que lance ValidationError con solo
		mensajes (sin message_dict) y comprobar que el view añade errores no-field.
		"""
		self.client.login(username=self.username, password=self.password)
		url = reverse('create_appointment')
		data = {
			'name': 'Sesión con error general',
			'price': '30.00',
			'duration': '60',
			'description': 'Forzar error general',
		}

		with patch('main.appointments.views.Appointment.full_clean', side_effect=ValidationError('Error general')):
			response = self.client.post(url, data)

		self.assertEqual(response.status_code, 200)
		form = response.context.get('form')
		self.assertIsNotNone(form)
		non_field = list(form.non_field_errors())
		self.assertTrue(non_field)
		self.assertIn('Error general', non_field[0])
		self.assertEqual(Appointment.objects.filter(name='Sesión con error general').count(), 0)

class UpdateAppointmentViewTests(TestCase):
	def setUp(self):
		self.username = 'staffuser'
		self.password = 'pass1234'
		self.user = User.objects.create_user(username=self.username, password=self.password)
		self.user.is_staff = True
		self.user.save()

		self.appointment = Appointment.objects.create(
			name='Sesión original',
			price=20.00,
			duration=30,
			description='Descripción original',
			premium=False,
			discount=0.00,
			endDiscount=None,
		)

	def _create_sample_appointment(self):
		return Appointment.objects.create(
			name='Original',
			price='20.00',
			duration=30,
			description='Original desc',
			premium=False,
			discount=0.00,
			endDiscount=None,
		)

	def test_get_update_shows_initial_values(self):
		self.client.login(username=self.username, password=self.password)
		appointment = self._create_sample_appointment()
		url = reverse('update_appointment', args=[appointment.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		form = response.context.get('form')
		self.assertIsNotNone(form)
		self.assertEqual(form.initial.get('name'), appointment.name)
		self.assertEqual(str(form.initial.get('price')), str(appointment.price))

	def test_post_update_valid_saves_and_redirects(self):
		self.client.login(username=self.username, password=self.password)
		appointment = self._create_sample_appointment()
		url = reverse('update_appointment', args=[appointment.id])
		data = {
			'name': 'Updated name',
			'price': '35.00',
			'duration': '90',
			'description': 'Updated desc',
			'premium': 'on',
		}
		response = self.client.post(url, data)
		self.assertEqual(response.status_code, 302)
		appointment.refresh_from_db()
		self.assertEqual(appointment.name, 'Updated name')
		self.assertEqual(str(appointment.price), '35.00')

	def test_post_update_full_clean_message_dict_adds_field_errors(self):
		self.client.login(username=self.username, password=self.password)
		appointment = self._create_sample_appointment()
		url = reverse('update_appointment', args=[appointment.id])
		data = {
			'name': 'Will fail',
			'price': '0.00',
			'duration': '30',
			'description': 'fail',
		}
		with patch('main.appointments.views.Appointment.full_clean', side_effect=ValidationError({'price': ['Precio inválido']})):
			response = self.client.post(url, data)

		self.assertEqual(response.status_code, 200)
		form = response.context.get('form')
		self.assertIsNotNone(form)
		self.assertTrue(form.errors)
		self.assertIn('price', form.errors)

	def test_post_update_full_clean_messages_adds_non_field_errors(self):
		self.client.login(username=self.username, password=self.password)
		appointment = self._create_sample_appointment()
		url = reverse('update_appointment', args=[appointment.id])
		data = {
			'name': 'Will fail general',
			'price': '10.00',
			'duration': '30',
			'description': 'fail general',
		}

		with patch('main.appointments.views.Appointment.full_clean', side_effect=ValidationError('Error general update')):
			response = self.client.post(url, data)

		self.assertEqual(response.status_code, 200)
		form = response.context.get('form')
		self.assertIsNotNone(form)
		non_field = list(form.non_field_errors())
		self.assertTrue(non_field)
		self.assertIn('Error general update', non_field[0])

	def test_post_update_full_clean_message_dict_unknown_field_adds_non_field_errors(self):
		"""Comprobar que si full_clean() lanza ValidationError con message_dict
		cuya clave no corresponde a ningún field del form, la vista añade
		esos mensajes como errores no-field.
		"""
		self.client.login(username=self.username, password=self.password)
		appointment = self._create_sample_appointment()
		url = reverse('update_appointment', args=[appointment.id])
		data = {
			'name': 'Will fail external',
			'price': '10.00',
			'duration': '30',
			'description': 'fail external',
		}

		with patch('main.appointments.views.Appointment.full_clean', side_effect=ValidationError({'external': ['Error externo update']})):
			response = self.client.post(url, data)

		self.assertEqual(response.status_code, 200)
		form = response.context.get('form')
		self.assertIsNotNone(form)
		non_field = list(form.non_field_errors())
		self.assertTrue(non_field)
		self.assertIn('Error externo update', non_field[0])
		
class DeleteAppointmentViewTests(TestCase):
    def setUp(self):
        self.username = 'staffuser'
        self.password = 'pass1234'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user.is_staff = True
        self.user.save()

        self.appointment = Appointment.objects.create(
            name='Sesión a eliminar',
            price=20.00,
            duration=30,
            description='Descripción de la sesión a eliminar',
            premium=False,
            discount=0.00,
            endDiscount=None,
        )
    def test_delete_appointment(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse('delete_appointment', args=[self.appointment.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Appointment.objects.filter(id=self.appointment.id).count(), 0)
		
class CreateDiscountViewTests(TestCase):
	def setUp(self):
		self.username = 'staffuser'
		self.password = 'pass1234'
		self.user = User.objects.create_user(username=self.username, password=self.password)
		self.user.is_staff = True
		self.user.save()

		self.appointment = Appointment.objects.create(
			name='Sesión con descuento',
			price=30.00,
			duration=40,
			description='Para pruebas de descuento',
			premium=False,
			discount=0.00,
			endDiscount=None,
		)

	def test_get_renders_form_initial_no_enddate(self):
		self.client.login(username=self.username, password=self.password)
		url = reverse('create_discount', args=[self.appointment.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertIn('form', response.context)
		form = response.context.get('form')
		self.assertIsNotNone(form)
		# initial discount debe venir del appointment
		self.assertEqual(form.initial.get('discount'), self.appointment.discount)
		# sin endDiscount debería mostrar texto "Sin fecha asignada"
		self.assertEqual(form.initial.get('current_end_date'), 'Sin fecha asignada')

	def test_get_renders_form_with_enddate(self):
		from django.utils import timezone
		# asignar una fecha de fin y comprobar que initial cambia
		self.appointment.endDiscount = timezone.now()
		self.appointment.save()
		self.client.login(username=self.username, password=self.password)
		url = reverse('create_discount', args=[self.appointment.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		form = response.context.get('form')
		self.assertIsNotNone(form)
		self.assertIsNotNone(form.initial.get('current_end_date'))
		self.assertNotEqual(form.initial.get('current_end_date'), 'Sin fecha asignada')

	def test_post_valid_updates_discount_and_redirects(self):
		self.client.login(username=self.username, password=self.password)
		url = reverse('create_discount', args=[self.appointment.id])
		data = {
			'discount': '5.00',
			'endDiscount': '',
		}
		response = self.client.post(url, data)
		self.assertEqual(response.status_code, 302)
		self.appointment.refresh_from_db()
		self.assertEqual(str(self.appointment.discount), '5.00')

	def test_post_with_endDiscount_sets_datetime(self):
		from django.utils import timezone
		self.client.login(username=self.username, password=self.password)
		url = reverse('create_discount', args=[self.appointment.id])
		# formato HTML5 datetime-local: YYYY-MM-DDTHH:MM
		future = (timezone.now() + timezone.timedelta(days=3)).replace(second=0, microsecond=0)
		formatted = future.strftime('%Y-%m-%dT%H:%M')
		data = {
			'discount': '7.50',
			'endDiscount': formatted,
		}
		response = self.client.post(url, data)
		self.assertEqual(response.status_code, 302)
		self.appointment.refresh_from_db()
		self.assertEqual(str(self.appointment.discount), '7.50')
		self.assertIsNotNone(self.appointment.endDiscount)

	def test_post_save_raises_validationerror_adds_non_field(self):
		self.client.login(username=self.username, password=self.password)
		url = reverse('create_discount', args=[self.appointment.id])
		data = {
			'discount': '3.00',
			'endDiscount': '',
		}
		with patch('main.appointments.views.Appointment.save', side_effect=ValidationError('Error general descuento')):
			response = self.client.post(url, data)
		self.assertEqual(response.status_code, 200)
		form = response.context.get('form')
		self.assertIsNotNone(form)
		non_field = list(form.non_field_errors())
		self.assertTrue(non_field)
		self.assertIn('Error general descuento', non_field[0])

	def test_post_save_validation_message_dict_field_and_non_field(self):
		self.client.login(username=self.username, password=self.password)
		url = reverse('create_discount', args=[self.appointment.id])
		data = {
			'discount': '2.00',
			'endDiscount': '',
		}
		# si message_dict tiene 'discount' debe añadirse como error de campo
		with patch('main.appointments.views.Appointment.save', side_effect=ValidationError({'discount': ['Descuento inválido']})):
			response = self.client.post(url, data)
		self.assertEqual(response.status_code, 200)
		form = response.context.get('form')
		self.assertIsNotNone(form)
		self.assertTrue(form.errors)
		self.assertIn('discount', form.errors)

	def test_post_save_message_dict_unknown_field_adds_non_field_errors(self):
		self.client.login(username=self.username, password=self.password)
		url = reverse('create_discount', args=[self.appointment.id])
		data = {
			'discount': '4.00',
			'endDiscount': '',
		}
		with patch('main.appointments.views.Appointment.save', side_effect=ValidationError({'external': ['Error externo descuento']})):
			response = self.client.post(url, data)
		self.assertEqual(response.status_code, 200)
		form = response.context.get('form')
		self.assertIsNotNone(form)
		non_field = list(form.non_field_errors())
		self.assertTrue(non_field)
		self.assertIn('Error externo descuento', non_field[0])


class AppointmentsViewTests(TestCase):
	def test_get_shows_appointments_and_now(self):
		a1 = Appointment.objects.create(
			name='A1', price=10.00, duration=30, description='', premium=False, discount=0.00, endDiscount=None
		)
		a2 = Appointment.objects.create(
			name='A2', price=20.00, duration=45, description='', premium=False, discount=0.00, endDiscount=None
		)

		url = reverse('appointments')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertIn('appointments', response.context)
		self.assertIn('now', response.context)
		qs = response.context['appointments']
		names = {o.name for o in qs}
		self.assertIn('A1', names)
		self.assertIn('A2', names)