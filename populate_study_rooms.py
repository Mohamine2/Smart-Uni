import os
import django
import random
from datetime import date, time

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from residence_connectee.models import Etudiant, Logement, Piece, ObjetConnecte, SalleEtude, Actualite

def populate_study_rooms():
    print("Début de la population de la base de données...")

    # --- 1. CRÉATION DES SALLES D'ÉTUDE ---
    salles_data = [
        {"nom": "Salle Turing", "capacite": 10, "description": "Zone calme avec écrans partagés."},
        {"nom": "Bibliothèque Nord", "capacite": 30, "description": "Silence absolu requis."},
        {"nom": "Espace Coworking", "capacite": 15, "description": "Idéal pour les projets de groupe."},
        {"nom": "Box Individuel A", "capacite": 1, "description": "Petit box pour entretiens visio."},
    ]

    for s in salles_data:
        SalleEtude.objects.get_or_create(nom=s['nom'], defaults=s)

    print("Population terminée avec succès !")

if __name__ == '__main__':
    populate_study_rooms()