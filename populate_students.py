import os
import django
from faker import Faker
import random
import string

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# N'oublie pas d'importer tous les modèles nécessaires
from residence_connectee.models import Etudiant, Logement, Piece, ObjetConnecte 

fake = Faker('fr_FR')

def generate_random_password(length=12):
    """Génère un mot de passe robuste mélangeant lettres et chiffres"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def populate(n=20):
    for i in range(n):
        # Génération des données de base
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        username = f"{first_name[0].lower()}{last_name.lower()}_{random.randint(10, 99)}"
        email = f"{username}@student.cytech.fr"
        phone = fake.phone_number()
        student_id = str(random.randint(20000000, 29999999))
        age = random.randint(17, 26)
        
        # Correction : Uniquement 'M' ou 'F' pour respecter les CHOIX_SEXE du modèle
        sex = random.choice(['M', 'F']) 

        raw_password = generate_random_password()

        user, created = Etudiant.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone_number': phone,
                'student_id': student_id,
                'age': age,
                'sex': sex,
                'is_active': True,
            }
        )

        if created:
            user.set_password(raw_password)
            user.save()
            print(f"Étudiant créé : {username} | Tel : {phone}")

            # --- 1. Création du Logement ---
            logement = Logement.objects.create(
                adresse=fake.street_address(),
                numero_logement=str(random.randint(1, 500)),
                occupant=user
            )

            # --- 2. Création des Pièces ---
            choix_pieces = ['Cuisine', 'Salon', 'Chambre', 'SDB']
            # On génère aléatoirement entre 2 et 4 pièces par logement
            nb_pieces = random.randint(2, 4)
            pieces_selectionnees = random.sample(choix_pieces, nb_pieces)

            for nom_piece in pieces_selectionnees:
                piece = Piece.objects.create(
                    nom=nom_piece,
                    logement=logement
                )

                # --- 3. Création des Objets Connectés ---
                choix_types_objets = ['Lampe', 'Thermostat', 'Prise']
                # On génère entre 1 et 3 objets connectés par pièce
                nb_objets = random.randint(1, 3)

                for _ in range(nb_objets):
                    type_objet = random.choice(choix_types_objets)
                    # On crée un nom logique (ex: "Lampe 1", "Prise 2", etc.)
                    nom_objet = f"{type_objet} {random.randint(1, 5)}"
                    
                    ObjetConnecte.objects.create(
                        nom=nom_objet,
                        type_objet=type_objet,
                        etat=random.choice([True, False]), # Allumé ou éteint aléatoirement
                        consommation=round(random.uniform(5.0, 150.0), 2), # Conso aléatoire
                        piece=piece
                    )
            
            print(f"  -> Logement n°{logement.numero_logement} généré avec {nb_pieces} pièces.")
            
        else:
            print(f"L'étudiant {username} existe déjà.")

if __name__ == '__main__':
    print("Début du peuplement de la base de données...")
    populate(20) 
    print("Opération terminée avec succès !")