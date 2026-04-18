from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from residence_connectee.models import Etudiant, Actualite, ObjetConnecte, Piece

# --- 1. MODULE ACCUEIL & ACTUALITÉS ---

def home_view(request):
    actus = Actualite.objects.all()

    cat_filtre = request.GET.get('categorie')
    if cat_filtre:
        actus = actus.filter(categorie=cat_filtre)

    ordre = request.GET.get('ordre', 'desc')
    if ordre == 'asc':
        actus = actus.order_by('date_publication')
    else:
        actus = actus.order_by('-date_publication')

    context = {
        'actus': actus,
        'categories': Actualite.CHOIX_CATEGORIE, 
        'selected_cat': cat_filtre,
        'selected_ordre': ordre,
        'pieces': Piece.objects.all(),
        'type_choices': ObjetConnecte.TYPE_CHOICES,
    }
    return render(request, 'index.html', context)

def detail_actualite(request, pk):
    actu = get_object_or_404(Actualite, pk=pk)
    return render(request, 'detail_actu.html', {'actu': actu})


# --- 2. MODULE AUTHENTIFICATION ---

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
            login(request, user)
            return redirect('dashboard')

    return render(request, 'register.html')
    
def login_view(request):
    if request.method == 'POST':
        user_nom = request.POST.get('username')
        user_password = request.POST.get('password')

        user = authenticate(request, username=user_nom, password=user_password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Identifiants invalides.")
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    return render(request, 'dashboard-simple.html', {'etudiant': request.user})


# --- 3. MODULE OBJETS CONNECTÉS ---

def recherche_objets(request):
    mot_cle = request.GET.get('q', '')
    type_objet_selectionne = request.GET.get('type_objet', '')
    etat_selectionne = request.GET.get('etat', '')
    piece_selectionnee = request.GET.get('piece', '')

    objets = ObjetConnecte.objects.all()

    if mot_cle:
        objets = objets.filter(nom__icontains=mot_cle)
    if type_objet_selectionne:
        objets = objets.filter(type_objet=type_objet_selectionne)
    if etat_selectionne == 'actif':
        objets = objets.filter(etat=True)
    elif etat_selectionne == 'inactif':
        objets = objets.filter(etat=False)
    if piece_selectionnee:
        objets = objets.filter(piece_id=piece_selectionnee)

    pieces = Piece.objects.all()

    context = {
        'objets': objets,
        'pieces': pieces,
        'mot_cle': mot_cle,
        'type_objet_selectionne': type_objet_selectionne,
        'etat_selectionne': etat_selectionne,
        'piece_selectionnee': piece_selectionnee,
        'type_choices': ObjetConnecte.TYPE_CHOICES,
    }

    return render(request, 'recherche_objets.html', context)

@login_required
def ajout_objet(request):
    mes_logements = request.user.logements.all()
    mes_pieces = Piece.objects.filter(logement__in=mes_logements)

    if request.method == 'POST':
        nom = request.POST.get('nom_objet')
        type_obj = request.POST.get('type_objet')
        piece_id = request.POST.get('piece')
        
        piece = get_object_or_404(mes_pieces, id=piece_id)
        
        ObjetConnecte.objects.create(
            nom=nom,
            type_objet=type_obj,
            piece=piece,
            etat=False
        )
        messages.success(request, "L'objet a été ajouté à votre logement.")
        return redirect('dashboard')

    context = {
        'pieces': mes_pieces,
        'type_choices': ObjetConnecte.TYPE_CHOICES,
    }
    return render(request, 'ajout_objet.html', context)

@login_required
def supprimer_objet(request, objet_id):
    objet = get_object_or_404(ObjetConnecte, id=objet_id)
    objet.delete()
    messages.success(request, "L'objet a été supprimé.")
    return redirect('dashboard')