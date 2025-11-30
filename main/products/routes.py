from django.urls import path
from django.conf import settings
from main.products import views
from django.conf.urls.static import static


urlpatterns = [
    path('productos/', views.list_products, name='list_products'),

    path('productos/gestion/', views.show_product_admin, name='show_products_admin'),
    path('productos/gestion/crear/', views.create_product_admin, name='create_product_admin'),
    path('productos/gestion/editar/<int:product_id>/', views.edit_product_admin, name='edit_product_admin'),
    path('productos/gestion/eliminar/<int:product_id>/', views.delete_product_admin, name='delete_product_admin'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)