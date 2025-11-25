from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from main.user.models import UserProfile
from .forms import ClientCreationForm, ClientLoginForm, UserUpdateForm, ProfileUpdateForm
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


@login_required
def profile(request):
    if not hasattr(request.user, 'userprofile'):
        UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            profile_obj = p_form.save(commit=False)
            
            if request.POST.get('delete_photo') == 'true':
                profile_obj.photo.delete(save=False)
                
                profile_obj.photo = None 
            
            profile_obj.save()
            
            messages.success(request, '¡Tu perfil ha sido actualizado!')
            return redirect('profile')
            
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.userprofile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'profile.html', context)