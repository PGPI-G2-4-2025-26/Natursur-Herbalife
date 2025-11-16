from django.shortcuts import render
from .forms import ClientCreationForm


def registration(request):
    form = ClientCreationForm()
    return render(request, 'registration.html', {'form': form})

def login(request):
    return render(request, 'login.html')