from django.contrib.auth.models import AbstractUser
from django.db import models

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

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"