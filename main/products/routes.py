from django.urls import path
from django.conf import settings

from main.products import views
from django.conf.urls.static import static


urlpatterns = [
    path('productos/', views.list_products, name='list_products'),
    path('carrito/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/', views.view_cart, name='view_cart'),
    path('solicitud/finalizar/', views.finalize_solicitation, name='finalize_solicitation'),
    
    path('solicitudes/mis/', views.my_solicitations, name='my_solicitations'), 
    path('admin/solicitudes/', views.admin_solicitations_list, name='admin_solicitations_list'), 
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)