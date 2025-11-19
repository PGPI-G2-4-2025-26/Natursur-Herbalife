from django.urls import path
from django.conf import settings

from main.appointments import views
from main.appointments import forms as form
from django.conf.urls.static import static


urlpatterns = [
    path('appointments/', views.appointments, name='appointments'),
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/update/<int:appointment_id>/', views.update_appointment, name='update_appointment'),
    path('appointments/delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('appointments/create_discount/<int:appointment_id>/', views.create_discount, name='create_discount'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)