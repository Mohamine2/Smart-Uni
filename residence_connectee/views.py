from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ObjetConnecte, Piece

from residence_connectee.models import Etudiant

def recherche_objets(request):
    objets = ObjetConnecte.objects.all()

    mot_cle = request.GET.get('q')
    type_objet = request.GET.get('type_objet')
    etat = request.GET.get('etat')
    piece_id = request.GET.get('piece')

    if mot_cle:
        objets = objets.filter(nom__icontains=mot_cle)

    if type_objet:
        objets = objets.filter(type_objet=type_objet)

    if etat:
        if etat == "actif":
            objets = objets.filter(etat=True)
        elif etat == "inactif":
            objets = objets.filter(etat=False)

    if piece_id:
        objets = objets.filter(piece_id=piece_id)

    pieces = Piece.objects.all()

    context = {
        'objets': objets,
        'pieces': pieces,
        'mot_cle': mot_cle or '',
        'type_objet_selectionne': type_objet or '',
        'etat_selectionne': etat or '',
        'piece_selectionnee': piece_id or '',
        'type_choices': ObjetConnecte.TYPE_CHOICES,
    }

    return render(request, 'recherche_objets.html', context)

def home_view(request):
    return render(request, 'index.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user_password = request.POST.get('password')
        user_first_name = request.POST.get('first_name')
        user_last_name = request.POST.get('last_name')
        user_phone = request.POST.get('phone')
        user_email = request.POST.get('email')
        user_student_id = request.POST.get('student_id')
        user_age = request.POST.get('age')
        user_sex = request.POST.get('sex')

        user, created = Etudiant.objects.get_or_create(
            username=username,
            defaults={
                'first_name': user_first_name,
                'last_name': user_last_name,
                'email': user_email,
                'phone_number': user_phone,
                'student_id': user_student_id,
                'age': user_age,
                'sex': user_sex,
                'is_active': True,
            }
        )

        if created:
            user.set_password(user_password)
            user.save()
            login(request, user) # Crée la session
            return redirect('dashboard')

    return render(request, 'register.html')
    
def login_view(request):
    if request.method == 'POST':
        user_nom = request.POST.get('username')
        user_password = request.POST.get('password')

        # authenticate vérifie le hash automatiquement
        user = authenticate(request, username=user_nom, password=user_password)

        if user is not None:
            login(request, user) # Crée la session
            return redirect('dashboard') # Redirige vers une page de succès
        else:
            messages.error(request, "Identifiants invalides.")
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required  # Cette ligne empêche les gens non-connectés d'entrer
def dashboard_view(request):
    # Ici, request.user contient l'étudiant qui vient de se connecter
    return render(request, 'dashboard-simple.html', {'etudiant': request.user})
