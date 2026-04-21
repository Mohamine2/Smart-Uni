from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from residence_connectee.models import Etudiant, Actualite, ObjetConnecte, Piece
from functools import wraps
from django.db.models import Sum

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
        password_confirm = request.POST.get('password_confirm') # On récupère le 2ème mot de passe
        user_first_name = request.POST.get('first_name')
        user_last_name = request.POST.get('last_name')
        user_phone = request.POST.get('phone')
        user_email = request.POST.get('email')
        user_student_id = request.POST.get('student_id')
        user_age = request.POST.get('age')
        user_sex = request.POST.get('sex')

        # VÉRIFICATION : Les mots de passe correspondent-ils ?
        if user_password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas. Veuillez réessayer.")
            return render(request, 'register.html')

        # On vérifie si l'utilisateur existe déjà
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
            messages.success(request, "Inscription réussie ! Veuillez vous connecter.")
            return redirect('login') 
        else:
            messages.error(request, "Ce pseudonyme est déjà utilisé. Veuillez en choisir un autre.")

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

@login_required
def modifier_profil(request):
    user = request.user
    if request.method == 'POST':
        # Récupération des données du formulaire
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone')
        user.age = request.POST.get('age')
        user.sex = request.POST.get('sex')
        
        user.save()
        messages.success(request, "Votre profil a été mis à jour avec succès !")
        return redirect('dashboard')

    return render(request, 'modifier_profil.html', {'user': user})

@login_required
def liste_etudiants(request):
    # On récupère tous les étudiants actifs qui ne sont pas des administrateurs
    etudiants = Etudiant.objects.filter(is_superuser=False, is_active=True).order_by('last_name', 'first_name')
    
    return render(request, 'liste_etudiants.html', {'etudiants': etudiants})


# Décorateur personnalisé pour vérifier les points
def niveau_requis(points_minimum):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.total_points >= points_minimum:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f"Niveau insuffisant. Il vous faut {points_minimum} points pour accéder à cette fonctionnalité.")
                return redirect('dashboard')
        return _wrapped_view
    return decorator


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

# --- DÉCORATEUR DE NIVEAU ---
def niveau_requis(niveau_min_valeur):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # On vérifie si la valeur du niveau de l'utilisateur est suffisante
            if request.user.niveau_valeur >= niveau_min_valeur:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Niveau insuffisant. Réclamez votre niveau supérieur sur votre tableau de bord !")
                return redirect('dashboard')
        return _wrapped_view
    return decorator


# --- FONCTION SÉCURITÉ : Vérifier la propriété de l'objet ---
def get_objet_if_owner(request, objet_id):
    """Récupère l'objet uniquement s'il appartient à l'utilisateur connecté"""
    objet = get_object_or_404(ObjetConnecte, id=objet_id)
    if objet.piece.logement.occupant != request.user:
        return None
    return objet


@login_required
def passer_niveau(request):
    if request.method == 'POST':
        user = request.user
        points = user.total_points
        
        if user.niveau == 'Débutant' and points >= 3:
            user.niveau = 'Intermédiaire'
            messages.success(request, "Bravo ! Vous avez débloqué le niveau Intermédiaire et l'ajout d'objets !")
        elif user.niveau == 'Intermédiaire' and points >= 5:
            user.niveau = 'Avancé'
            messages.success(request, "Bravo ! Niveau Avancé atteint. Vous pouvez maintenant régler et supprimer vos objets.")
        elif user.niveau == 'Avancé' and points >= 7:
            user.niveau = 'Expert'
            messages.success(request, "Félicitations ! Vous êtes devenu Expert. Les statistiques sont débloquées.")
        else:
            messages.error(request, "Vous n'avez pas encore assez de points pour réclamer ce niveau.")
            
        user.save()
    return redirect('dashboard')


# === NIVEAU 3 : INTERMÉDIAIRE (Ajout / Renommage) ===

@login_required
@niveau_requis(1)
def ajout_objet(request):
    mes_logements = request.user.logements.all()
    mes_pieces = Piece.objects.filter(logement__in=mes_logements)

    if request.method == 'POST':
        nom = request.POST.get('nom_objet')
        type_obj = request.POST.get('type_objet')
        piece_id = request.POST.get('piece')
        
        piece = get_object_or_404(mes_pieces, id=piece_id)
        
        ObjetConnecte.objects.create(nom=nom, type_objet=type_obj, piece=piece, etat=False)
        messages.success(request, "L'objet a été ajouté à votre logement.")
        return redirect('dashboard')

    context = {'pieces': mes_pieces, 'type_choices': ObjetConnecte.TYPE_CHOICES}
    return render(request, 'ajout_objet.html', context)


@login_required
@niveau_requis(1)
def renommer_objet(request, objet_id):
    objet = get_objet_if_owner(request, objet_id)
    if not objet:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')

    if request.method == 'POST':
        nouveau_nom = request.POST.get('nouveau_nom')
        if nouveau_nom:
            objet.nom = nouveau_nom
            objet.save()
            messages.success(request, "L'objet a été renommé avec succès.")
            return redirect('dashboard')
            
    return render(request, 'renommer_objet.html', {'objet': objet})


# === NIVEAU 5 : AVANCÉ (Suppression / Réglages) ===

@login_required
@niveau_requis(2)
def supprimer_objet(request, objet_id):
    objet = get_objet_if_owner(request, objet_id)
    if not objet:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
        
    objet.delete()
    messages.success(request, "L'objet a été supprimé.")
    return redirect('dashboard')


@login_required
@niveau_requis(2)
def regler_objet(request, objet_id):
    objet = get_objet_if_owner(request, objet_id)
    if not objet:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')

    if request.method == 'POST':
        # On gère l'état (On/Off)
        nouvel_etat = request.POST.get('etat') == 'on'
        objet.etat = nouvel_etat
        
        # On peut simuler une modification de consommation en fonction de l'état
        if nouvel_etat:
            objet.consommation = float(request.POST.get('puissance', 50.0))
        else:
            objet.consommation = 0.0
            
        objet.save()
        messages.success(request, f"Les réglages de {objet.nom} ont été mis à jour.")
        return redirect('dashboard')

    return render(request, 'regler_objet.html', {'objet': objet})


# === NIVEAU 7 : EXPERT (Statistiques) ===

@login_required
@niveau_requis(3)
def statistiques_conso(request):
    mes_logements = request.user.logements.all()
    mes_objets = ObjetConnecte.objects.filter(piece__logement__in=mes_logements)
    
    # 1. On utilise la base de données pour faire la somme
    agregation = mes_objets.aggregate(total=Sum('consommation'))
    
    # 2. Sécurité : Si aucun objet n'existe, on met 0.0. Sinon, on force en float
    if agregation['total'] is None:
        conso_totale = 0.0
    else:
        conso_totale = float(agregation['total'])
    
    # 3. Objets allumés vs éteints
    objets_actifs = mes_objets.filter(etat=True)
    objets_inactifs = mes_objets.filter(etat=False)

    context = {
        'conso_totale': conso_totale,
        'nb_actifs': objets_actifs.count(),
        'nb_inactifs': objets_inactifs.count(),
        'objets_actifs': objets_actifs,
    }
    return render(request, 'statistiques.html', context)