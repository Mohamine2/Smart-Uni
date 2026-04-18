from django.contrib import admin
from .models import Etudiant, Logement, Piece, ObjetConnecte, Actualite

class ObjetConnecteInline(admin.TabularInline):
    model = ObjetConnecte
    extra = 0
    fields = ('nom', 'type_objet', 'etat', 'consommation')

class PieceInline(admin.TabularInline):
    model = Piece
    extra = 0
    show_change_link = True 

class LogementInline(admin.StackedInline):
    model = Logement
    extra = 0
    show_change_link = True

@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('username', 'last_name', 'niveau', 'total_points')
    fieldsets = (
        ('Informations Personnelles', {
            'fields': ('username', 'first_name', 'last_name', 'email', 'phone_number', 'student_id', 'age', 'sex')
        }),
        ('Statistiques & Niveaux', {
            'fields': ('points_connexion', 'points_consultation')
        }),
    )
    inlines = [LogementInline]

@admin.register(Logement)
class LogementAdmin(admin.ModelAdmin):
    list_display = ('numero_logement', 'occupant', 'adresse')
    inlines = [PieceInline]
    
    def has_module_permission(self, request):
        return False

@admin.register(Piece)
class PieceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'logement', 'afficher_objets_count')
    inlines = [ObjetConnecteInline]

    def afficher_objets_count(self, obj):
        return f"{obj.objets.count()} objet(s)"
    afficher_objets_count.short_description = "Nombre d'objets"

    def has_module_permission(self, request):
        return False

# --- NOUVEAU MODULE : ACTUALITÉS ---
@admin.register(Actualite)
class ActualiteAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'date_publication')
    list_filter = ('categorie', 'date_publication')
    search_fields = ('titre', 'contenu')