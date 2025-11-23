from django.urls import path
from django.conf import settings
from main.products import views
from django.conf.urls.static import static


urlpatterns = [
    path('productos/', views.list_products, name='list_products'),
    path('carrito/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/', views.view_cart, name='view_cart'),
    path('solicitud/finalizar/', views.finalize_solicitation, name='finalize_solicitation'),
    path('pedidos/', views.show_orders, name='my_orders'),
    path('pedidos/admin/', views.show_orders_admin, name='show_orders_admin'),
    path('pedidos/<int:order_id>/detalles/', views.order_detail, name='order_detail'),
    path('pedidos/<int:order_id>/editar/', views.edit_order, name='edit_order'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)