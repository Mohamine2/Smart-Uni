from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def home_view(request):
    return render(request, 'index.html')

def register_view(request):
    return render(request, 'register.html')
    
def login_view(request):
    if request.method == 'POST':
        user_nom = request.POST.get('username')
        user_mdp = request.POST.get('password')

        # authenticate vérifie le hash automatiquement
        user = authenticate(request, username=user_nom, password=user_mdp)

        if user is not None:
            login(request, user) # Crée la session
            return redirect('dashboard') # Redirige vers une page de succès
        else:
            messages.error(request, "Identifiants invalides.")
    
    return render(request, 'login.html')

@login_required  # Cette ligne empêche les gens non-connectés d'entrer
def dashboard_view(request):
    # Ici, request.user contient l'étudiant qui vient de se connecter
    return render(request, 'dashboard-simple.html', {'etudiant': request.user})
