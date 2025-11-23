from django.shortcuts import render, redirect
from .forms import ClientCreationForm, ClientLoginForm
from django.contrib.auth import logout, login as auth_login
from django.conf import settings

def registration(request):
    if request.method == 'POST':
        form = ClientCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            
            auth_login(request, user)
            return redirect('home') 
            
    else:
        form = ClientCreationForm()

    return render(request, 'registration.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = ClientLoginForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home') 
            
    else:
        form = ClientLoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Renderiza la plantilla de confirmación en GET y realiza logout en POST."""
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return render(request, 'logout.html')


def profile(request):
    return render(request, 'profile.html')
