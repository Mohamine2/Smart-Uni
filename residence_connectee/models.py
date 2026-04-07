from django.contrib.auth.models import AbstractUser
from django.db import models

class Etudiant(AbstractUser):
    # Les champs nom, prenom, email et password sont déjà inclus dans AbstractUser
    # On ajoute uniquement le téléphone
    telephone = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"