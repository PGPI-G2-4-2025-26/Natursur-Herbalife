from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from main import views 
from django.conf.urls.static import static
from django.views.static import serve 


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('cuentas/', include('django.contrib.auth.urls')), 
    path('registro/', views.registration, name='registration'), 
    path('login/', views.login, name='login'),
    
    path('', views.home, name='home'), 
    path('servicios/', views.services, name='services'), 
    
    path('productos/', views.list_products, name='list_products'),
    path('carrito/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/', views.view_cart, name='view_cart'),
    path('solicitud/finalizar/', views.finalize_solicitation, name='finalize_solicitation'),
    
    path('solicitudes/mis/', views.my_solicitations, name='my_solicitations'), 
    path('admin/solicitudes/', views.admin_solicitations_list, name='admin_solicitations_list'), 
    
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)