from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone # Nécessaire pour les dates des actualités

class Etudiant(AbstractUser):
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    student_id = models.CharField(max_length=20, unique=True, null=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    
    CHOIX_SEXE = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    sex = models.CharField(max_length=1, choices=CHOIX_SEXE, null=True, blank=True)

    points_connexion = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    points_consultation = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def total_points(self):
        return self.points_connexion + self.points_consultation

    @property
    def niveau(self):
        total = self.total_points
        if total >= 7: return "Expert"
        if total >= 5: return "Avancé"
        if total >= 3: return "Intermédiaire"
        return "Débutant"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Niveau : {self.niveau} ({self.total_points} pts)"

class Logement(models.Model):
    adresse = models.CharField(max_length=255)
    numero_logement = models.CharField(max_length=10)
    occupant = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='logements'
    )

    def __str__(self):
        return f"Logement {self.numero_logement} ({self.occupant.username})"

class Piece(models.Model):
    NOM_CHOICES = [
        ('Cuisine', 'Cuisine'), 
        ('Salon', 'Salon'), 
        ('Chambre', 'Chambre'), 
        ('SDB', 'Salle de Bain')
    ]
    nom = models.CharField(max_length=50, choices=NOM_CHOICES)
    logement = models.ForeignKey(Logement, on_delete=models.CASCADE, related_name='pieces')

    def __str__(self):
        return f"{self.nom} - Logement {self.logement.numero_logement}"

class ObjetConnecte(models.Model):
    TYPE_CHOICES = [('Lampe', 'Lampe'), ('Thermostat', 'Thermostat'), ('Prise', 'Prise')]
    nom = models.CharField(max_length=100)
    type_objet = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True, null=True)
    etat = models.BooleanField(default=False)
    consommation = models.FloatField(default=0.0)
    piece = models.ForeignKey(Piece, on_delete=models.CASCADE, related_name='objets')

    def __str__(self):
        return f"{self.nom} ({self.piece.nom})"

# --- NOUVEAU MODULE : ACTUALITÉS ---
class Actualite(models.Model):
    CHOIX_CATEGORIE = [
        ('RESIDENCE', 'Vie de la résidence'),
        ('LOCAL', 'Infos Locales'),
        ('URGENT', 'Alerte / Maintenance'),
    ]

    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    image = models.ImageField(upload_to='actualites/', blank=True, null=True)
    date_publication = models.DateTimeField(default=timezone.now)
    categorie = models.CharField(max_length=50, choices=CHOIX_CATEGORIE, default='RESIDENCE')

    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"
        ordering = ['-date_publication']