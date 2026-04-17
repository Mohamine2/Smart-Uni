from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal

class Etudiant(AbstractUser):
    # Les champs nom, prenom, email et password sont déjà inclus dans AbstractUser
    phone_number = models.CharField(max_length=30, blank=True, null=True)

    # Numéro étudiant (Unique pour éviter les doublons)
    student_id = models.CharField(max_length=20, unique=True, null=True)
    
    # Âge (On utilise PositiveIntegerField pour éviter les nombres négatifs)
    age = models.PositiveIntegerField(null=True, blank=True)
    
    # Sexe (Utilisation de choix pour restreindre les possibilités)
    CHOIX_SEXE = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    sex = models.CharField(max_length=1, choices=CHOIX_SEXE, null=True, blank=True)

    points_connexion = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    points_consultation = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def total_points(self):
        """Calcule la somme des points de connexion et de consultation."""
        return self.points_connexion + self.points_consultation

    @property
    def niveau(self):
        """Détermine le niveau en fonction du système de points défini."""
        total = self.total_points
        if total >= 7: return "Expert"
        if total >= 5: return "Avancé"
        if total >= 3: return "Intermédiaire"
        return "Débutant"

    def __str__(self):
        # On affiche aussi le niveau dans la représentation texte
        return f"{self.first_name} {self.last_name} - Niveau : {self.niveau} ({self.total_points} pts)"