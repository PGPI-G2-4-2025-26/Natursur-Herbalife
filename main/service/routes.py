from django.urls import path
from django.conf import settings
from main import views 
from django.conf.urls.static import static


urlpatterns = [
    path('servicios/', views.services, name='services'), 
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)