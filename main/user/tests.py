from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from main.user.views import login
from django.core.exceptions import ValidationError
from main.user.validators import (
    CustomUserAttributeSimilarityValidator,
    CustomMinimumLengthValidator,
    CustomNumericPasswordValidator,
    CustomCommonPasswordValidator,
)

class RegistrationViewTests(TestCase):
    def test_registration_get_renders_form(self):
        url = reverse('registration')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration.html')

    def test_registration_post_creates_user_and_logs_in(self):
        url = reverse('registration')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Testpass1234',
            'password2': 'Testpass1234',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        user_qs = User.objects.filter(username='testuser')
        self.assertTrue(user_qs.exists())
        user = user_qs.first()

        session = self.client.session
        self.assertIn('_auth_user_id', session)
        self.assertEqual(str(user.pk), str(session['_auth_user_id']))
    def test_registration_post_invalid_data_shows_errors(self):
        url = reverse('registration')
        data = {
            'username': '',  # missing username
            'email': 'invalid-email',  # invalid email
            'password1': 'short',  # too short password
            'password2': 'mismatch',  # passwords do not match
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # form re-rendered with errors

        form = None
        if hasattr(response, 'context') and response.context is not None:
            form = response.context.get('form')

        self.assertIsNotNone(form, 'Se esperaba encontrar `form` en el contexto de la respuesta.')

        self.assertIn('username', form.errors)
        self.assertIn('El nombre de usuario es obligatorio.', form.errors['username'])

        self.assertIn('email', form.errors)
        self.assertIn('Por favor, introduce un correo válido.', form.errors['email'])
        self.assertIn('password2', form.errors)
        combined_password_errors = ' '.join(form.errors['password2'])
        self.assertTrue('contraseña' in combined_password_errors.lower() or "don't match" in combined_password_errors.lower())

class LoginFunctionViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _add_session_to_request(self, request):
        middleware = SessionMiddleware(get_response=lambda req: None)
        middleware.process_request(request)
        request.session.save()

    def test_login_view_function_valid_credentials_logs_in_and_redirects(self):
        username = 'funcuser'
        password = 'FuncPass123'
        User.objects.create_user(username=username, email='func@example.com', password=password)

        data = {'username': username, 'password': password}
        request = self.factory.post(reverse('login'), data)
        self._add_session_to_request(request)
        request.user = AnonymousUser()

        response = login(request)

        self.assertEqual(response.status_code, 302)

        session = request.session
        user = User.objects.get(username=username)
        self.assertIn('_auth_user_id', session)
        self.assertEqual(str(user.pk), str(session['_auth_user_id']))

    def test_login_view_function_invalid_credentials_rerenders_form(self):
        username = 'funcuser2'
        password = 'CorrectFunc123'
        User.objects.create_user(username=username, email='func2@example.com', password=password)

        data = {'username': username, 'password': 'WrongPass'}
        request = self.factory.post(reverse('login'), data)
        self._add_session_to_request(request)
        request.user = AnonymousUser()

        response = login(request)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Usuario o contraseña incorrectos.', content)
    
    def test_login_view_function_get_renders_empty_form(self):
        request = self.factory.get(reverse('login'))
        request.user = AnonymousUser()

        response = login(request)

        self.assertEqual(response.status_code, 200)

class LogoutViewTests(TestCase):
    def test_logout_get_renders_confirmation(self):
        url = reverse('logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logout.html')

    def test_logout_post_logs_out_and_redirects(self):
        username = 'logoutuser'
        password = 'LogoutPass123'
        User.objects.create_user(username=username, email='logout@example.com', password=password)

        logged_in = self.client.login(username=username, password=password)
        self.assertTrue(logged_in)

        url = reverse('logout')
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))

        session = self.client.session
        self.assertNotIn('_auth_user_id', session)
class ProfileViewTests(TestCase):
    def setUp(self):
        self.username = 'profileuser'
        self.password = 'ProfilePass123'
        self.user = User.objects.create_user(username=self.username, email='profile@example.com', password=self.password)

    def test_profile_get_creates_userprofile_and_renders_forms(self):

        self.client.login(username=self.username, password=self.password)

        self.user.userprofile.delete()

        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(hasattr(self.user, 'userprofile'))

        self.assertIn('u_form', response.context)
        self.assertIn('p_form', response.context)

    def test_profile_post_updates_user_and_profile_and_shows_message(self):
        self.client.login(username=self.username, password=self.password)

        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '+34123456789',
        }
        response = self.client.post(reverse('profile'), data)

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.userprofile.phone, '+34123456789')

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('¡Tu perfil ha sido actualizado!' in str(m) for m in messages))

    def test_profile_post_delete_photo_removes_file(self):
        self.client.login(username=self.username, password=self.password)
        profile = self.user.userprofile

        img = SimpleUploadedFile('photo.jpg', b'JPEGDATA', content_type='image/jpeg')
        profile.photo.save('photo.jpg', img, save=True)
        self.assertTrue(profile.photo)

        data = {
            'first_name': self.user.first_name or '',
            'last_name': self.user.last_name or '',
            'phone': profile.phone or '',
            'delete_photo': 'true',
        }
        response = self.client.post(reverse('profile'), data)
        self.assertEqual(response.status_code, 302)

        profile.refresh_from_db()
        self.assertFalse(profile.photo)

class ValidatorsTests(TestCase):
    def test_custom_user_similarity_allows_digits(self):
        v = CustomUserAttributeSimilarityValidator()
        v.validate('1234567890')

    def test_custom_user_similarity_allows_common_passwords(self):
        v = CustomUserAttributeSimilarityValidator()
        v.validate('password')

    def test_minimum_length_validator_raises(self):
        v = CustomMinimumLengthValidator(min_length=8)
        with self.assertRaises(ValidationError) as cm:
            v.validate('short')
        exc = cm.exception
        self.assertTrue('8' in str(exc))
        self.assertEqual(getattr(exc, 'code', None), 'password_too_short')

    def test_numeric_password_validator_raises(self):
        v = CustomNumericPasswordValidator()
        with self.assertRaises(ValidationError) as cm:
            v.validate('123456789')
        exc = cm.exception
        self.assertIn('La contraseña no puede contener solo números', str(exc))
        self.assertEqual(getattr(exc, 'code', None), 'password_entirely_numeric')

    def test_common_password_validator_raises_on_common(self):
        v = CustomCommonPasswordValidator()
        with self.assertRaises(ValidationError) as cm:
            v.validate('password')
        exc = cm.exception
        self.assertIn('Esa contraseña es muy común', str(exc))
        self.assertEqual(getattr(exc, 'code', None), 'password_too_common')

    def test_common_password_validator_allows_digits(self):
        v = CustomCommonPasswordValidator()
        v.validate('12345678') 

    
