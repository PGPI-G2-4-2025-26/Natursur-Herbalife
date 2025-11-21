from django.shortcuts import render, redirect
from .forms import ClientCreationForm
from django.contrib.auth import logout


def registration(request):
    if request.method == 'POST':
        form = ClientCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = ClientCreationForm()

    return render(request, 'registration.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login # Usamos un alias 'auth_login' para evitar conflictos de nombres
from .forms import ClientLoginForm # Asegúrate de importar tu formulario personalizado

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
