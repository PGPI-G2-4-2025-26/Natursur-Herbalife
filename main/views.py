from django.shortcuts import render
from django.conf import settings

from .testimonial.models import Testimonial

def home(request):
    testimonials = Testimonial.objects.all()[:1] 
    context = {
        'testimonials': testimonials,
        'MEDIA_URL': settings.MEDIA_URL 
    }
    return render(request, 'home.html', context)

def services(request):
    return render(request, 'services.html') 