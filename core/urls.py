# core/urls.py
from django.contrib import admin
from django.urls import path
from residence_connectee import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('index/', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard-simple/', views.dashboard_view, name='dashboard'),
    path('profil/modifier/', views.modifier_profil, name='modifier_profil'),
    
    # --- MODULE ACTUALITÉS ---
    path('actualites/<int:pk>/', views.detail_actualite, name='detail_actu'),
    
    # --- MODULE OBJETS CONNECTÉS ---
    path('objets/recherche/', views.recherche_objets, name='recherche_objets'),

    path('profil/passer-niveau/', views.passer_niveau, name='passer_niveau'),
    
    # NIVEAU 3 (Intermédiaire)
    path('objets/ajouter/', views.ajout_objet, name='ajout_objet'),
    path('objets/renommer/<int:objet_id>/', views.renommer_objet, name='renommer_objet'),
    
    # NIVEAU 5 (Avancé)
    path('objets/supprimer/<int:objet_id>/', views.supprimer_objet, name='supprimer_objet'),
    path('objets/regler/<int:objet_id>/', views.regler_objet, name='regler_objet'),
    
    # NIVEAU 7 (Expert)
    path('statistiques/', views.statistiques_conso, name='statistiques'),
]