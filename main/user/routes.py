from django.urls import path
from django.conf import settings
from main.user import views
from main.user import forms as user_forms
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html', authentication_form=user_forms.ClientLoginForm), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registration, name='registration'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)