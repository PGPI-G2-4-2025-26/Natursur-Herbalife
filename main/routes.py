from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from main import views 
from django.conf.urls.static import static
from django.views.static import serve 


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', views.home, name='home'), 
    
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),

    path('', include('main.user.routes')),
    path('', include('main.service.routes')),
    path('', include('main.products.routes')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)