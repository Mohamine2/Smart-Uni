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
    
    # --- MODULE ACTUALITÉS ---
    path('actualites/<int:pk>/', views.detail_actualite, name='detail_actu'),
    
    # --- MODULE OBJETS CONNECTÉS ---
    path('objets/recherche/', views.recherche_objets, name='recherche_objets'),
    path('objets/ajouter/', views.ajout_objet, name='ajout_objet'),
    path('objets/supprimer/<int:objet_id>/', views.supprimer_objet, name='supprimer_objet'),
]