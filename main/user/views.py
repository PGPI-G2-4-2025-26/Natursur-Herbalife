from django.shortcuts import render, redirect
from .forms import ClientCreationForm


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