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


def login(request):
    return render(request, 'login.html')


def logout_view(request):
    """Renderiza la plantilla de confirmación en GET y realiza logout en POST."""
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return render(request, 'logout.html')

def profile(request):
    return render(request, 'profile.html')
