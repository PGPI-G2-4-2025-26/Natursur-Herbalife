from django.urls import path, include
from django.conf import settings
from main.user import views
from django.conf.urls.static import static


urlpatterns = [
    path('cuentas/', include('django.contrib.auth.urls')), 
    path('registro/', views.registration, name='registration'), 
    path('login/', views.login, name='login'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)